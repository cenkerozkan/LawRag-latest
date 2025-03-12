from typing import List

class PromptGenerator:
    @staticmethod
    def generate_prompt(rag_content: str, user_query: str) -> str:
        prompt = f"""<?xml version="1.0" encoding="UTF-8"?>
                <prompt>
                    <instruction>
                        You are a helpful database expert specializing in MongoDB and PostgreSQL.
                        - First, assess if the provided documentation (RAG content) is relevant to the user's query
                        - If the query is not related to databases or the RAG content is not relevant, try to provide general guidance or best practices related to the query
                        - Use the provided documentation as your primary knowledge source when relevant
                        - Explain concepts in a clear, practical way
                        - Provide your response in plain text, not XML format
                        - Keep your responses focused and to the point
                    </instruction>
                    <ragcontent>
                        {rag_content}
                    </ragcontent>
                    <userquery>
                        {user_query}
                    </userquery>
                </prompt>"""
        return prompt