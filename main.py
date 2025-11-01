from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
#from langchain_core.output_parsers import PydanticOutputParse
from langchain.agents.structured_output import ToolStrategy
from langchain_core.tools import Tool
from langchain.agents import create_agent
from typing import Optional

load_dotenv() 

class finalReciept(BaseModel):
    # After everything is done will return the use with final order price and delivery time
    deliveryMethod: str
    pickUpLocation: Optional[str] = None
    deliveryAddress: Optional[str] = None

llm2 = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
llm1 = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
#parser = PydanticOutputParser(pydantic_object=ResearchResponse)

#Tool function that will ask user for pick up or delivery
def pickUpOrDeliver(*args, **kwargs):
    while True:
        user = input("Would you like to pick up your order or have it delivered? ")
        prompt = f"""user said {user} determine if they want "pick up" or "delivery". Only respond with either "pick up" if user means pick up or "delivery" if user means delivery one of these two words but if the user doesn't mean pick up and doesn't mean delivery just say "invalid choice"  """
        
        response = llm2.invoke(prompt).content.lower()

        if response == "pick up":
            return "pick up"
        elif response == "delivery":
            return "delivery"
        else:
            print("Invalid choice. Please choose either 'pick up' or 'delivery'.")

def pickUplocation(*args, **kwargs):
    while True:
        location = input("Please provide your pick-up location: ")
        prompt = f"""user said {location} determine if this is a valid pick up location and if it is valid responde with 'valid pick up location' else respond with 'invalid pick up location', our valid locations are "jane and finch", "downtown toronto", and \"scarborough town centre\""""
        response = llm2.invoke(prompt).content.lower()
        print(f"[Debug] LLM response: {response}")
        if response == "valid pick up location":
            return location
        else:
            print("invalid pick up location")

def deliverylocation(*args, **kwargs):
    while True:
        location = input("Please provide your delivery location: ")
        prompt = f"user said {location} is their delivery address please ask them again if this is their address if it follows the right connatation which is number then adresss then if they say yes respond with 'valid' else respond with 'invalid'"
        response = llm2.invoke(prompt).content.lower()
        if response == "valid":
            return location
        else:
            print("invalid")
    

PickOrDel = Tool(
    name="get_pickordel_method",
    func=pickUpOrDeliver,
    description="MUST be called first. Determines whether user wants 'pick up' or 'delivery'."
)

pickUpLocation_tool = Tool(
    name="get_pickup_location",
    func=pickUplocation,
    description="ONLY used if 'get_pickordel_method' returned 'pick up'."
)

deliveryLocation_tool = Tool(
    name="get_delivery_address",
    func=deliverylocation,
    description="ONLY used if 'get_pickordel_method' returned 'delivery'."
)





#Our actual agent that will use the llm and prompt defined above
agent = create_agent(
    model=llm1,
    system_prompt = 
    """You are a customer service agent for a food delivery service. Your task is to assist customers in placing their orders by determining their preferred delivery method and gathering necessary details based on their choice.
    Follow these guidelines:
    1. First, use the 'get_pickordel_method' tool to ask the customer whether they would like to pick up their order or have it delivered.
    2. If the customer chooses 'pick up', use the 'get_pickup_location' tool to obtain their preferred pick-up location.
    3. If the customer chooses 'delivery', use the 'get_delivery_address' tool to collect their delivery address.
    4. After gathering the required information, compile the final order details including the delivery method and either the pick-up location or delivery address.
    5. Always ensure to confirm the details with the customer before finalizing the order.
    """,
    response_format=ToolStrategy(finalReciept),
    tools=[PickOrDel, pickUpLocation_tool, deliveryLocation_tool],
    )

print("="*64)
print("CUSTOMER SERVICE AGENT")
print("="*64)

result = agent.invoke({"messages": [("user", "Hi, I'd like to place an order")]})

print("\n" + "="*64)
print("FINAL RESULT")
print("="*64)
print(result)