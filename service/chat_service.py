import datetime
import os
import traceback

from google import genai
from google.genai.types import GenerateContentResponse

from db.model.chat_thread_model import ChatThreadModel
from db.model.pdf_content_model import PdfContentModel
from db.model.message_model import MessageModel
from repository.context_repository import ContextRepository
from util.logger import get_logger
from util.prompt_generator import prompt_generator
from agents.web_search_agent import web_search_agent
from agents.pdf_analyzer_agent import pdf_analyzer_agent
from config.config import MESSAGE_HISTORY_SIZE


class ChatService:
    def __init__(self):
        self._logger = get_logger(__name__)
        self._prompt_generator = prompt_generator

        try:
            self._gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            self._web_search_agent = web_search_agent
            self._pdf_analyzer_agent = pdf_analyzer_agent
            self._context_repository = ContextRepository()

        except Exception as e:
            self._logger.error(f"Error initializing RagService: {e}")

    async def _retrieve_web_search_content(
            self,
            query: str,
            contents: list
    ) -> list[dict[str, str]]:
        web_search_result: list[dict[str, str]] = []
        try:
            self._logger.info(f"Web search started for query: {query}")
            web_search_result = await self._web_search_agent.search_web(query, contents)
        except Exception as e:
            self._logger.error(f"Error during web search: {e}")
        return web_search_result

    async def _update_chat_thread(
            self,
            chat_thread: ChatThreadModel
    ) -> bool:
        is_updated: bool = False
        chat_thread.updated_at = datetime.datetime.now().isoformat()
        self._logger.info(f"Updating chat thread: {chat_thread.chat_id}")
        update_crud_result = await self._context_repository.update_one(chat_thread)
        if not update_crud_result:
            self._logger.error(f"Failed to update chat thread: {chat_thread.chat_id}")
            is_updated = False
        if update_crud_result:
            self._logger.info(f"Chat thread updated successfully: {chat_thread.chat_id}")
            is_updated = True
        return is_updated

    async def run(
            self,
            query: str,
            chat_thread: ChatThreadModel,
            web_search: bool
    ) -> dict:
        result: dict = {
            "code": 0,
            "success": False,
            "message": "",
            "error": "",
            "data": {}
        }
        web_search_results: list[dict[str, str]]
        web_sources: list[str] | None = None
        pdf_content: list[PdfContentModel] = []

        # Fetch contents (context history or message history you can say).
        contents: list = [str({"role": msg.role, "content": msg.content}) for msg in
                          chat_thread.history[-MESSAGE_HISTORY_SIZE:]]

        if len(chat_thread.pdf_content) > 0:
            pdf_content = chat_thread.pdf_content

        # Generate system instructions
        prompt: str = self._prompt_generator.generate_chat_agent_prompt(user_query=query, pdf_content=pdf_content)

        # If web search is asked.
        if web_search:
            web_search_results = await self._retrieve_web_search_content(query, contents)
            contents.extend([str(result) for result in web_search_results])
            web_sources = [result.get("page_url", "") for result in web_search_results if result is not None]

        # Generate content with Gemini.
        try:
            contents.append(prompt)
            response: GenerateContentResponse = await self._gemini_client.aio.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=contents
            )
        except Exception as e:
            result.update({"code": 200,
                           "success": False,
                           "message": "Sistemde yaşanan bir aksaklık sebebiyle şu an size yardımcı olamıyorum.",
                           "error": str(e),
                           "data": {
                               "response": "Sistemde yaşanan bir aksaklık sebebiyle şu an size yardımcı olamıyorum."}})
            self._logger.error(f"Error generating response: {e}")
            return result

        # Only update chat thread if the gemini response is successful.
        # Create a new message model and update them accordingly.
        chat_thread.history.append(MessageModel(created_at=datetime.datetime.now().isoformat(), role="user",
                                                content=query, web_sources=None))
        chat_thread.history.append(MessageModel(created_at=datetime.datetime.now().isoformat(), role="ai",
                                                content=response.text,
                                                web_sources=web_sources))

        _: bool = await self._context_repository.update_one(chat_thread)
        # Try three more times, then leave it.
        if not _:
            for i in range(3):
                self._logger.error(f"Something went wrong while updating chat thread: {chat_thread.chat_id}")
                is_updated = await self._update_chat_thread(chat_thread)
                if is_updated:
                    result.update({
                        "code": 200,
                        "success": True,
                        "message": "RAG Sorgusu başarıyla tamamlandı.",
                        "data": {"response": response.text}})
                    break
                if i == 2:
                    self._logger.error(f"Failed to update chat thread after 3 attempts: {chat_thread.chat_id}")
                    result.update({"success": False, "message": "Sohbet sırasında bir şeyler ters gitti!.",
                                   "data": {"response": "Şu anda size yardımcı olamıyorum."}})
                    return result
        result.update({"code": 200, "success": True, "message": "RAG query processed successfully",
                       "data": {"response": response.text}})
        return result

chat_service = ChatService()