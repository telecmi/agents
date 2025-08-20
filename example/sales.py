# user_bot.py

import asyncio
from piopiy.agent import Agent, current_room, current_token
from piopiy.transports.services.telecmi import TeleCMITransport, TeleCMIParams
from dotenv import load_dotenv
import os

load_dotenv()
# ... other imports

async def create_session():
    
    


    transport = TeleCMITransport(
        params=TeleCMIParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
        )
    )

    # ... session logic

async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session
    )
    await agent.start()

if __name__ == "__main__":
    asyncio.run(main())