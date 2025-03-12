import os

from langchain_chroma import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_google_genai import GoogleGenerativeAIEmbeddings


from meta.singleton import Singleton
from util.logger import get_logger


class PdfSelector(metaclass=Singleton):
    def __init__(self):
        self._logger = get_logger(__name__)
        self._examples: list = [
            {"input": "How do you insert a document into a MongoDB collection?", "output": "mongodb"},
            {"input": "How can you update multiple documents at once in MongoDB?", "output": "mongodb"},
            {"input": "What is the difference between find() and findOne()?", "output": "mongodb"},
            {"input": "How do you delete a document from a MongoDB collection?", "output": "mongodb"},
            {"input": "What are the different ways to insert data into a MongoDB collection?", "output": "mongodb"},
            {"input": "How do you insert multiple documents at once?", "output": "mongodb"},
            {"input": "What happens if you insert a document without specifying _id?", "output": "mongodb"},
            {"input": "How do you handle duplicate key errors when inserting documents?", "output": "mongodb"},
            {"input": "How can you insert a document with a specific _id value?", "output": "mongodb"},
            {"input": "What is the difference between insertOne() and insertMany()?", "output": "mongodb"},
            {"input": "How can you improve the performance of bulk inserts in MongoDB?", "output": "mongodb"},
            {"input": "How do you retrieve all documents from a collection?", "output": "mongodb"},
            {"input": "How do you filter documents based on a specific field value?", "output": "mongodb"},
            {"input": "How do you retrieve only specific fields from a document?", "output": "mongodb"},
            {"input": "How do you use comparison operators like $gt, $lt, and $eq in queries?", "output": "mongodb"},
            {"input": "How do you query documents using an array field?", "output": "mongodb"},
            {"input": "How do you perform a text search in MongoDB?", "output": "mongodb"},
            {"input": "How do you use the $in operator to find documents matching multiple values?", "output": "mongodb"},
            {"input": "How can you implement pagination in MongoDB queries?", "output": "mongodb"},
            {"input": "How do you sort query results in ascending or descending order?", "output": "mongodb"},
            {"input": "What is a projection in MongoDB, and how can you use it?", "output": "mongodb"},
            {"input": "What is the difference between updateOne() and updateMany()?", "output": "mongodb"},
            {"input": "How do you update a specific field in a document?", "output": "mongodb"},
            {"input": "How do you increment a numeric field in a document?", "output": "mongodb"},
            {"input": "What is the difference between $set and $unset operators?", "output": "mongodb"},
            {"input": "How do you update an array field in a document?", "output": "mongodb"},
            {"input": "How do you add an element to an array in a document?", "output": "mongodb"},
            {"input": "How do you remove an element from an array in a document?", "output": "mongodb"},
            {"input": "How do you update a document only if a specific condition is met?", "output": "mongodb"},
            {"input": "What is the purpose of the upsert option in an update operation?", "output": "mongodb"},
            {"input": "How do you use $push vs. $addToSet for updating arrays?", "output": "mongodb"},
            {"input": "How do you update nested fields within an embedded document?", "output": "mongodb"},
            {"input": "What happens if you try to update a document that doesn't exist and don't use upsert?", "output": "mongodb"},
            {"input": "What is the difference between deleteOne() and deleteMany()?", "output": "mongodb"},
            {"input": "How do you delete all documents from a collection?", "output": "mongodb"},
            {"input": "How do you delete documents based on a condition?", "output": "mongodb"},
            {"input": "How do you delete a field from a document instead of deleting the whole document?", "output": "mongodb"},
            {"input": "How do you use findOneAndDelete() to remove and return a document?", "output": "mongodb"},
            {"input": "How can you safely delete all documents while preserving the collection?", "output": "mongodb"},
            {"input": "How do you insert a row into a PostgreSQL table?", "output": "postgresql"},
            {"input": "How can you update multiple rows at once in PostgreSQL?", "output": "postgresql"},
            {"input": "What is the difference between SELECT and SELECT DISTINCT?", "output": "postgresql"},
            {"input": "How do you delete a row from a PostgreSQL table?", "output": "postgresql"},
            {"input": "What are the different ways to insert data into a PostgreSQL table?", "output": "postgresql"},
            {"input": "How do you insert multiple rows at once?", "output": "postgresql"},
            {"input": "What happens if you insert a row without specifying a primary key?", "output": "postgresql"},
            {"input": "How do you handle duplicate key errors when inserting rows?", "output": "postgresql"},
            {"input": "How can you insert a row with a specific ID value?", "output": "postgresql"},
            {"input": "What is the difference between INSERT INTO and COPY FROM?", "output": "postgresql"},
            {"input": "How can you improve the performance of bulk inserts in PostgreSQL?", "output": "postgresql"},
            {"input": "How do you retrieve all rows from a table?", "output": "postgresql"},
            {"input": "How do you filter rows based on a specific column value?", "output": "postgresql"},
            {"input": "How do you retrieve only specific columns from a table?", "output": "postgresql"},
            {"input": "How do you use comparison operators like >, <, and = in queries?", "output": "postgresql"},
            {"input": "How do you query rows using an array column?", "output": "postgresql"},
            {"input": "How do you perform a text search in PostgreSQL?", "output": "postgresql"},
            {"input": "How do you use the IN operator to find rows matching multiple values?", "output": "postgresql"},
            {"input": "How can you implement pagination in PostgreSQL queries?", "output": "postgresql"},
            {"input": "How do you sort query results in ascending or descending order?", "output": "postgresql"},
            {"input": "What is a projection in PostgreSQL, and how can you use it?", "output": "postgresql"},
            {"input": "What is the difference between UPDATE and UPDATE ... RETURNING?", "output": "postgresql"},
            {"input": "How do you update a specific column in a row?", "output": "postgresql"},
            {"input": "How do you increment a numeric column in a row?", "output": "postgresql"},
            {"input": "What is the difference between SET and DEFAULT when updating rows?", "output": "postgresql"},
            {"input": "How do you update a JSONB column in PostgreSQL?", "output": "postgresql"},
            {"input": "How do you add an element to an array column in PostgreSQL?", "output": "postgresql"},
            {"input": "How do you remove an element from an array column in PostgreSQL?", "output": "postgresql"},
            {"input": "How do you update a row only if a specific condition is met?", "output": "postgresql"},
            {"input": "What is the purpose of the ON CONFLICT clause in an update operation?", "output": "postgresql"},
            {"input": "How do you use jsonb_set() to update JSONB data in PostgreSQL?", "output": "postgresql"},
            {"input": "How do you update nested fields within a JSONB column?", "output": "postgresql"},
            {"input": "What happens if you try to update a row that doesn't exist and don't use INSERT ON CONFLICT?","output": "postgresql"},
            {"input": "What is the difference between DELETE FROM and TRUNCATE?", "output": "postgresql"},
            {"input": "How do you delete all rows from a table?", "output": "postgresql"},
            {"input": "How do you delete rows based on a condition?", "output": "postgresql"},
            {"input": "How do you delete a column from a row instead of deleting the whole row?","output": "postgresql"},
            {"input": "How do you use DELETE ... RETURNING to remove and return a row?", "output": "postgresql"},
            {"input": "How can you safely delete all rows while preserving the table structure?","output": "postgresql"}
        ]

    def _remove_duplicates(self, result: list[dict]) -> list[str]:
        unique_result = []
        for res in result:
            if "output" in res and res["output"] not in unique_result:
                unique_result.append(res["output"])
        return unique_result

    async def aselect(
            self,
            question: dict[str, str]
    ) -> list[str]:
        # There is a cache problem in langchain and I cannot find it.
        # It makes the whole process a bit more slower. but it is not a big problem.
        example_selector = SemanticSimilarityExampleSelector.from_examples(
            self._examples,
            GoogleGenerativeAIEmbeddings(model="models/text-embedding-004",
                                         google_api_key=os.getenv("GEMINI_API_KEY")),
            Chroma,
            k=2
        )
        example_selector_results: list[dict] = await example_selector.aselect_examples(question)
        results: list[str] = self._remove_duplicates(example_selector_results)
        return results