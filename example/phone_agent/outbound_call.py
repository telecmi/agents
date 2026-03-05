import os
import dotenv
from piopiy_voice import RestClient

dotenv.load_dotenv()

def trigger_outbound_call():
    """
    This script triggers an outbound call to a customer and connects them to the Phone Agent.
    Requirements:
    - PIOPIY_TOKEN: Your Piopiy REST API Token (from the dashboard)
    - AGENT_ID: The ID of your Piopiy Voice Agent
    - PIOPIY_NUMBER: Your purchased Piopiy phone number (e.g. +15551234567)
    - CUSTOMER_NUMBER: The destination phone number to call (e.g. +15557654321)
    """
    token = os.getenv("PIOPIY_TOKEN")
    agent_id = os.getenv("AGENT_ID")
    caller_id = os.getenv("PIOPIY_NUMBER")
    to_number = os.getenv("CUSTOMER_NUMBER")

    if not all([token, agent_id, caller_id, to_number]):
        print("❌ Error: Missing required environment variables.")
        print("Please ensure PIOPIY_TOKEN, AGENT_ID, PIOPIY_NUMBER, and CUSTOMER_NUMBER are set.")
        return

    # Initialize the Piopiy REST Client
    client = RestClient(token=token)

    print(f"📞 Triggering outbound call to {to_number} from {caller_id}...")
    
    try:
        # Trigger an Outbound AI Agent Call
        response = client.ai.call(
            caller_id=caller_id,
            to_number=to_number,
            agent_id=agent_id,
            variables={
                "customer_name": "Alice", # This is passed to create_session as metadata
            }
        )
        print("✅ Call successfully initiated!")
        print(response)
    except Exception as e:
        print(f"❌ Failed to initiate call: {e}")

if __name__ == "__main__":
    trigger_outbound_call()
