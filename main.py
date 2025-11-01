from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
#from langchain_core.output_parsers import PydanticOutputParse
from langchain.agents.structured_output import ToolStrategy
from langchain_core.tools import Tool
from langchain.agents import create_agent


load_dotenv() 

#llm1 = ChatOpenAI(model = "gpt-4-mini")
#response1 = llm1.invoke("Hey chat how are you?")

class deliveryResponse(BaseModel):
    # After everything is done will return the use with final order price and delivery time
    deliveryMethod: str


llm2 = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
#parser = PydanticOutputParser(pydantic_object=ResearchResponse)

#Tool function that will ask user for pick up or delivery
def pickUpOrDeliver(*args, **kwargs):
    while True:
        user = input("Would you like to pick up your order or have it delivered? ")
        prompt = f"""user said {user} determine if they want "pick up" or "delivery". Only respond with either "pick up" if user means pick up or "delivery" if user means delivery one of these two words but if the user doesn't mean pick up and doesn't mean delivery just say "invalid choice"  """
       
        response = llm2.invoke(prompt).content.lower()
        print(f"[Debug] LLM response: {response}") 
        
        if response == "pick up":
            return "pick up"
        elif response == "delivery":
            return "delivery"
        else:
            print("Invalid choice. Please choose either 'pick up' or 'delivery'.")

delivery_tool = Tool(
    name="deliveryMethod",
    func=pickUpOrDeliver,
    description="Gives us the delivery method (pick up or delivery)."
)


#Our actual agent that will use the llm and prompt defined above
agent = create_agent(
    model=llm2,
    system_prompt ="You are a helpful customer service agent. When asked about delivery method, you MUST use the get_delivery_method tool to ask the user for their preference. After getting their answer, confirm their choice.",
    response_format=ToolStrategy(deliveryResponse),
    tools=[delivery_tool]
    )

print("=== Customer Service Agent ===\n")

result = agent.invoke({"messages": [("user", "Hi, I'd like to place an order")]})

print("\n=== RESULT ===")
structured =  result['structured_response'].deliveryMethod
print(structured)