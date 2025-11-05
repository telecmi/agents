# Pinecone info voice agent with function calling
# Path: agents/example/function_calling/pinecone_search_agent.py
import asyncio
import os
from dotenv import load_dotenv
from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.adapters.schemas.function_schema import FunctionSchema
from piopiy.audio.vad.silero import SileroVADAnalyzer
from piopiy.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.deepgram.tts import DeepgramTTSService
from piopiy.services.llm_service import FunctionCallParams
from pinecone import Pinecone
from openai import OpenAI

load_dotenv()

# Initialize clients once at module level
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---- Tool handler ----
async def search_pinecone(params: FunctionCallParams):
    try:
        global pc, openai_client
        args = getattr(params, "args", {}) or {}
        query = args.get("query", "")
        
        if not query:
            await params.result_callback({"error": "Query cannot be empty"})
            return
        
        index_name = os.getenv("PINECONE_INDEX_NAME")
        if not index_name:
            await params.result_callback({"error": "Missing Pinecone index name"})
            return
        
        # Connect to Pinecone index
        index = pc.Index(index_name)
        
        # Get embedding for query text
        embedding = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        ).data[0].embedding
        
        # Query Pinecone index
        results = index.query(
            vector=embedding, 
            top_k=3, 
            include_metadata=True
        )
        
        # Extract results
        if not results.matches:
            await params.result_callback({
                "query": query,
                "message": "No results found",
                "top_results": []
            })
            return
        
        summaries = []
        for match in results.matches:
            text = match.metadata.get("text", "No text")
            summaries.append({
                "text": text,
                "score": float(match.score)
            })
        
        await params.result_callback({
            "query": query,
            "top_results": summaries
        })

        
    except Exception as e:
        print(f"Error in search_pinecone: {e}")
        await params.result_callback({
            "error": f"Search failed: {str(e)}"
        })

# ---- Tool schema ----
pinecone_function = FunctionSchema(
    name="search_pinecone",
    description="Anything reagarding Telecmi, call this function to search the Pinecone knowledge base for relevant information.",
    properties={
        "query": {
            "type": "string",
            "description": "It gives relevant information about Telecmi.",
        }
    },
    required=["query"],
)

# ---- Session factory ----
async def create_session():
    voice_agent = VoiceAgent(
        instructions="You are a helpful assistant with access to a knowledge base. When users ask questions, use the search_pinecone function to find relevant information and provide accurate answers based on the search results.",
        greeting="Hello! I can help you search our knowledge base. What would you like to know?",
    )
    
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
    tts = DeepgramTTSService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    
    # Add Pinecone search tool
    voice_agent.add_tool(pinecone_function, search_pinecone)
    
    vad = SileroVADAnalyzer()
    
    await voice_agent.Action(
        stt=stt,
        llm=llm,
        tts=tts,
        vad=vad,
        allow_interruptions=True,
        interruption_strategy=MinWordsInterruptionStrategy(min_words=1),
    )
    
    await voice_agent.start()

# ---- Entrypoint ----
async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
    )
    await agent.connect()

if __name__ == "__main__":
    print("AGENT_ID:", os.getenv("AGENT_ID"))
    asyncio.run(main())