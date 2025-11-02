from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
#from langchain_core.output_parsers import PydanticOutputParse
from langchain.agents.structured_output import ToolStrategy
from langchain_core.tools import Tool
from langchain.agents import create_agent
from typing import Optional, List, Dict
from typing import Optional
import re
import ast
import json
import pyttsx3
import speech_recognition as sr

#Our yapper 
nyapper = pyttsx3.init()
rate = nyapper.getProperty('rate')
nyapper.setProperty('rate', rate - 50)  
nyapper.setProperty('volume', 1)  
voices = nyapper.getProperty('voices')
nyapper.setProperty('voice', voices[0].id)

def say_prompt(text:str):
    print(text)
    nyapper.say(text)

load_dotenv() 

menu = {
    "Margherita Pizza": [10.0, "Classic pizza with tomato sauce, mozzarella, and basil.", ], 
    "Pepperoni Pizza": [12.0, "Tomato sauce, mozzarella, and pepperoni slices.", ],
    "Veggie Pizza": [11.0, "Tomato sauce, mozzarella, bell peppers, onions, mushrooms, and olives.", ],
    "BBQ Chicken Pizza": [13.0, "BBQ sauce, mozzarella, grilled chicken, red onions, and cilantro.", ],
    "Hawaiian Pizza": [12.0, "Tomato sauce, mozzarella, ham, and pineapple chunks.", ],
}

# Keep the most recently collected order so tools that receive unexpected
# arguments (e.g. a phone number) can still compute the total.
last_order_items: Dict[str, int] = {}

class orderItem(BaseModel):
    # An item in the order with its name and quantity
    itemName: str
    quantity: int
    price: float

class finalReciept(BaseModel):
    # After everything is done will return the use with final order price and delivery time
    name: str
    phoneNumber: str
    deliveryMethod: str
    pickUpLocation: Optional[str] = None
    deliveryAddress: Optional[str] = None
    orderDetails: List [orderItem] = []
    totalPrice: float
    deliveryTime: int


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
#parser = PydanticOutputParser(pydantic_object=ResearchResponse)

#Tool function that will ask user for their name
def name (*args, **kwargs):
    while True:
        say_prompt("What is your name?")
        name = input("You: ")
        prompt = f"""user said {name} is their name please confirm that this is a valid name if it is respond with 'valid name' else respond with 'invalid name'"""
        response = llm.invoke(prompt).content.lower()
        if response == "valid name":
            return name
        else:
            print("invalid name")

#Tool function that will ask user for their phone number
def phoneNumber(*args, **kwargs):
    while True:
        say_prompt("What is your phone number?")
        phone = input("You:")
        prompt = f"""user said {phone} is their phone number please confirm that this is a valid phone number 10 numbers either words or numbers respond with 'valid phone number' else respond with 'invalid phone number'"""
        response = llm.invoke(prompt).content.lower()
        if response == "valid phone number":
            return phone
        else:
            print("invalid phone number")

#Tool function that will ask user for pick up or delivery
def pickUpOrDeliver(*args, **kwargs):
    while True:
        say_prompt("Would you like to pick up your order or have it delivered? ")
        user = input("You: ")
        prompt = f"""
        The user said: "{user}"

        Task:
        1. Decide if the user wants to **pick up** their order or have it **delivered**.
        2. Output **only one word**, exactly as follows:
        - "pick up" → if the user will come to pick up the food.
        - "delivery" → if the user wants the food delivered.
        - "invalid" → if it’s unclear or something else.

        Do NOT add any explanation, punctuation, or extra words.  
        Your entire response must be exactly one of: pick up, delivery, invalid.
        """        
        response = llm.invoke(prompt).content.lower()

        if response == "pick up":
            return "pick up"
        elif response == "delivery":
            return "delivery"
        else:
            print("Invalid choice. Please choose either 'pick up' or 'delivery'.")

def pickUplocation(*args, **kwargs):
    while True:

        say_prompt("Please provide your pick-up location: ")
        location = input("You: ")
        prompt = f"""
        The user said: "{location}"

        Task:
        1. Determine if this is a valid pick-up location.
        2. The valid locations are:
        - "Jane and Finch"
        - "Downtown Toronto"
        - "Scarborough Town Centre"
        3. The user’s input may contain spelling mistakes or minor variations. Try to match it to the closest valid location.
        4. Output **only one phrase**, exactly as follows:
        - "valid pick up location" → if it matches one of the valid locations.
        - "invalid pick up location" → if it does not match any valid location.

        Do NOT add any explanation, extra words, or punctuation.  
        Your response must be exactly one of: valid pick up location, invalid pick up location.
        """        
        response = llm.invoke(prompt).content.lower()
        print(f"[Debug] LLM response: {response}")
        if response == "valid pick up location":
            return location
        else:
            print("invalid pick up location")

def deliverylocation(*args, **kwargs):
    while True:
        
        say_prompt("Please provide your delivery location: ")
        location = input("You: ")
        prompt = f"user said {location} is their delivery address if it looks like a real address respond with 'valid' else respond with 'invalid'"
        response = llm.invoke(prompt).content.lower()
        if response == "valid":
            return location
        else:
            print("invalid")
    

def parse_order_dict(response: str) -> dict:
    match = re.search(r"\{.*\}", response, re.DOTALL)
    if match:
        try:
            return ast.literal_eval(match.group())
        except:
            pass
    return {}



def actualOrder(menu: dict, *args, **kwargs) -> Dict[str, int]:
    order_items = {}
    conversation = []
    print("\nAvailable menu items:")
    for item, (price, desc) in menu.items():
        print(f"- {item}: ${price:.2f} - {desc}")
    print("\nWhat would you like to order? Feel free to ask questions about our menu items!")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() == "done":
            if not order_items:
                say_prompt("Your order is empty! Please tell me what you'd like to order.")
                continue
                
            print("\nYour current order:")
            for item, qty in order_items.items():
                price = menu[item][0] * qty
                print(f"- {qty}x {item} (${price:.2f})")
            total = sum(menu[item][0] * qty for item, qty in order_items.items())
            print(f"\nTotal: ${total:.2f}")
            confirm = input("Is this correct? (yes/no): ").lower()
            if confirm == "yes":
                break
            else:
                print("Ok, let's continue with your order.")
                continue

        # Add user input to conversation history
        conversation.append(f"User: {user_input}")
        
        # First, let's understand the user's intent
        intent_prompt = (
            "You are a knowledgeable pizza restaurant assistant. Analyze the following customer message:\n"
            f"Customer: {user_input}\n\n"
            "Determine if they are:\n"
            "1. Asking about menu items/ingredients/prices\n"
            "2. Placing or modifying an order\n"
            "3. Making general conversation\n"
            "Respond ONLY with the number (1, 2, or 3)"
        )
        
        intent = llm.invoke(intent_prompt).content.strip()
        
        if intent == "1":
            # Handle menu questions
            menu_prompt = (
                "You are a pizza expert. Answer the following customer question about our menu:\n"
                f"Menu:\n{json.dumps(menu, indent=2)}\n\n"
                f"Customer question: {user_input}\n\n"
                "Provide a helpful, knowledgeable response focusing on ingredients, prices, and recommendations."
            )
            answer = llm.invoke(menu_prompt).content
            print(f"\nAssistant: {answer}\n")
            continue
            
        elif intent == "2":
            # Handle order placement/modification
            order_prompt = (
                "You are a pizza order assistant. Extract the order details from this conversation.\n"
                f"Menu items:\n{json.dumps(menu, indent=2)}\n\n"
                f"Current order: {order_items}\n"
                f"Customer input: {user_input}\n\n"
                "Instructions:\n"
                "1. Consider the customer's exact wording and intention\n"
                "2. If they want to modify existing items, account for that\n"
                "3. Return ONLY a Python dictionary with menu item names as keys and final quantities as values\n"
                "4. Use exact menu item names\n"
                "Example: {'Pepperoni Pizza': 2, 'Margherita Pizza': 1}\n"
            )
            
            try:
                response = llm.invoke(order_prompt).content
                conversation.append(f"Assistant: {response}")
                
                parsed = parse_order_dict(response)
                if parsed:
                    # Validate all items exist in menu
                    valid_items = {}
                    invalid_items = []
                    
                    for item, qty in parsed.items():
                        if item in menu:
                            try:
                                qty_num = int(qty)
                                if qty_num >= 0:  # Allow zero for removals
                                    valid_items[item] = qty_num
                            except (ValueError, TypeError):
                                print(f"Invalid quantity for {item}")
                        else:
                            invalid_items.append(item)
                    
                    if invalid_items:
                        suggestion_prompt = (
                            f"The customer asked for '{', '.join(invalid_items)}' but these aren't on our menu.\n"
                            f"Our menu items are: {', '.join(menu.keys())}\n"
                            "Suggest the closest menu item(s) that match what they want."
                        )
                        suggestion = llm.invoke(suggestion_prompt).content
                        print(f"\nAssistant: {suggestion}")
                        continue
                    
                    # Update the order with valid items
                    order_items = valid_items  # Replace with new state
                    if order_items:
                        print("\nYour updated order:")
                        for item, qty in order_items.items():
                            price = menu[item][0] * qty
                            print(f"- {qty}x {item} (${price:.2f})")
                        total = sum(menu[item][0] * qty for item, qty in order_items.items())
                        print(f"\nTotal: ${total:.2f}")
                        print("\nWhat else would you like? (say 'done' to finish)")
                else:
                    clarification_prompt = (
                        f"The customer said: '{user_input}'\n"
                        "Generate a helpful response asking for clarification about their order.\n"
                        "Include an example of how they could phrase their order."
                    )
                    clarification = llm.invoke(clarification_prompt).content
                    print(f"\nAssistant: {clarification}")
            except Exception as e:
                print("I apologize for the confusion. Could you please rephrase your order?")
                print("For example: 'I'd like 2 Pepperoni Pizzas' or 'one Margherita please'")
        
        else:
            # Handle general conversation
            chat_prompt = (
                "You are a friendly pizza restaurant assistant. Respond to the customer's message:\n"
                f"Customer: {user_input}\n\n"
                "Provide a friendly response and guide them toward making an order if appropriate."
            )
            response = llm.invoke(chat_prompt).content
            print(f"\nAssistant: {response}\n")
    
    return order_items



def get_total_price(order_items: Dict[str, int], menu=menu) -> float:
    """Compute total price for an order.

    Accepts several common input shapes to be defensive:
    - dict: {"Item Name": quantity, ...}
    - list of dicts: [{"itemName": ..., "quantity": ...}, ...] or [{"Item Name": qty}, ...]
    - string repr of a dict (will attempt to parse)

    Returns a float rounded to 2 decimals.
    """
    total = 0.0

    # If caller didn't pass usable order items, fall back to last collected order
    global last_order_items
    if not order_items:
        if last_order_items:
            order_items = last_order_items
        else:
            return 0.0

    # If it's a string, try to parse a dict out of it
    if isinstance(order_items, str):
        # If agent passed a phone number or other single-string arg, try fallback
        parsed = parse_order_dict(order_items)
        if parsed:
            return get_total_price(parsed, menu=menu)
        # If the string looks like a 10-digit phone, use last order
        if re.fullmatch(r"\d{10}", order_items.strip()):
            if last_order_items:
                return get_total_price(last_order_items, menu=menu)
            return 0.0

    # Dict -> straightforward mapping
    if isinstance(order_items, dict):
        # update global last_order_items for later fallback
        try:
            # ensure quantities are ints
            normalized = {k: int(v) for k, v in order_items.items()}
        except Exception:
            normalized = order_items
        last_order_items = normalized
        # use normalized for computation
        order_items = normalized
        for item, qty in order_items.items():
            # Normalize quantity to a number
            try:
                quantity = int(qty)
            except Exception:
                try:
                    quantity = float(qty)
                except Exception:
                    # If quantity can't be parsed, skip
                    continue

            price = 0.0
            m = menu.get(item)
            if isinstance(m, (list, tuple)) and len(m) > 0:
                price = float(m[0])
            elif isinstance(m, (int, float)):
                price = float(m)

            total += price * quantity

        return round(total, 2)

    # List/tuple -> handle lists of dicts or simple names
    if isinstance(order_items, (list, tuple)):
        for entry in order_items:
            if isinstance(entry, dict):
                # Common structured keys
                if "quantity" in entry and ("itemName" in entry or "item" in entry or "name" in entry):
                    name = entry.get("itemName") or entry.get("item") or entry.get("name")
                    qty = entry.get("quantity")
                    try:
                        quantity = int(qty)
                    except Exception:
                        try:
                            quantity = float(qty)
                        except Exception:
                            continue

                    m = menu.get(name)
                    price = float(m[0]) if isinstance(m, (list, tuple)) and len(m) > 0 else (float(m) if isinstance(m, (int, float)) else 0.0)
                    total += price * quantity
                else:
                    # Maybe dict like {"Item Name": qty}
                    for k, v in entry.items():
                        try:
                            quantity = int(v)
                        except Exception:
                            try:
                                quantity = float(v)
                            except Exception:
                                continue
                        m = menu.get(k)
                        price = float(m[0]) if isinstance(m, (list, tuple)) and len(m) > 0 else (float(m) if isinstance(m, (int, float)) else 0.0)
                        total += price * quantity
            else:
                # entry could be a plain item name (assume quantity 1)
                name = str(entry)
                m = menu.get(name)
                price = float(m[0]) if isinstance(m, (list, tuple)) and len(m) > 0 else (float(m) if isinstance(m, (int, float)) else 0.0)
                total += price * 1

        return round(total, 2)

    # Fallback: try to parse any serializable representation
    try:
        parsed = parse_order_dict(str(order_items))
        if parsed:
            return get_total_price(parsed, menu=menu)
    except Exception:
        pass

    return round(total, 2)

GreetingName = Tool(
    name="get_name",
    func=name,
    description=" MUST be called first asks the user for their name and validates it."
)

GreentingPhone = Tool(
    name="get_phone_number",
    func=phoneNumber,
    description="MUST be called after we get their nameAsks the user for their phone number and validates it."
)


PickOrDel = Tool(
    name="get_pickordel_method",
    func=pickUpOrDeliver,
    description="MUST be called after getting basic information. Determines whether user wants 'pick up' or 'delivery'."
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

getOrder_tool = Tool(
    name="get_order_details",
    func=lambda *args, **kwargs: actualOrder(menu, *args, **kwargs),
    description="Collects the user's order details including items, quantities, and prices."
)


getTotalPrice_tool = Tool(
    name="get_total_price",
    func=get_total_price,
    description="Calculates totalPrice from order items."
)


#Our actual agent that will use the llm and prompt defined above
agent = create_agent(
    model=llm,
    system_prompt = """
    You are a friendly food ordering assistant. Guide the user through ordering pizza in a conversational way.
    You MUST follow this exact sequence:
    1. Call get_name to get customer name
    2. Call get_phone_number for contact info
    3. Call get_pickordel_method to ask if they want pick up or delivery
    4. Based on their choice:
       - If "pick up": Call get_pickup_location
       - If "delivery": Call get_delivery_address
    5. Call get_order_details to collect their pizza order
    6. Call getTotalPrice_tool to calculate the final price
    7. Create and return a finalReciept with all collected information

    IMPORTANT:
    - Call ONE tool at a time and wait for its result
    - Actually run each tool - do not skip steps
    - Use the exact tool responses to build the receipt
    - Do not invent or guess any values
    - Be conversational and friendly between steps

    When returning the finalReciept, make sure all fields are properly filled:
    - name (string): from get_name
    - phoneNumber (string): from get_phone_number
    - deliveryMethod (string): from get_pickordel_method
    - pickUpLocation (string, optional): from get_pickup_location if delivery method is 'pick up'
    - deliveryAddress (string, optional): from get_delivery_address if delivery method is 'delivery'
    - orderDetails (list of orderItem): from get_order_details
    - totalPrice (float): from getTotalPrice_tool
    - deliveryTime (int): estimated time in minutes (default 30)
    """,
    response_format=ToolStrategy(finalReciept),
    tools=[GreetingName, GreentingPhone, PickOrDel, pickUpLocation_tool, deliveryLocation_tool, getOrder_tool, getTotalPrice_tool],
    )


print("Welcome to the Pizza Ordering System!")

print("=" * 64)
print("CUSTOMER SERVICE AGENT")
print("=" * 64)

conversation_history = []

conversation_history = [("user", "hi")]

result = agent.invoke({"messages": conversation_history})
print(result["structured_response"])
