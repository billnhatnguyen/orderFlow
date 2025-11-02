import os
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
#import pyttsx3 strayed away due to eleven labs being
import speech_recognition as sr
import firebase_admin
from firebase_admin import credentials, db
import datetime
import time
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play

cred = credentials.Certificate("./orderflow-6b892-firebase-adminsdk-fbsvc-6a6c495452.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://orderflow-6b892-default-rtdb.firebaseio.com/'})
ref = db.reference()

# Initialize text-to-speech engine
def initialize_tts():
    try:
        engine = pyttsx3.init()
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate - 20)
        engine.setProperty('volume', 1.0)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[6].id)
        return engine

    except Exception as e:
        print(f"TTS initialization error: {e}")
        return None
r = sr.Recognizer()

def speakUp(prompt: str = None) -> str:
    if prompt:
        say_prompt(prompt)
    with sr.Microphone() as source: 
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            return "reprompt me please"

        languages = ["en-EN"]

        for lang in languages:
            try:
                text = r.recognize_google(audio, language=lang)
                print(f"You said: {text}")
                return text
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                return "reprompt me please"
        return "reprompt me please"


# Global TTS engine
nyapper = initialize_tts()

#def say_prompt(text: str):
#    """Speaks the text using TTS. Returns None (doesn't return the text)."""
#    if not text:
#        return
#        
#    print(f"[TTS]: {text}")
#    global nyapper
#    
#    for attempt in range(3):  # Try 3 times
#        try:
#            if nyapper is None:
#                nyapper = initialize_tts()
#                if nyapper is None:
#                    return
#            
#            # Stop any ongoing speech
#            try:
#                nyapper.stop()
#            except:
#                pass
#            
#            # Clear the queue
#            if hasattr(nyapper, '_inLoop') and nyapper._inLoop:
#                nyapper.endLoop()
#            
#            # Speak the text
#            nyapper.say(text)
#            nyapper.runAndWait()
#            
#            # Add small delay to ensure completion
#            time.sleep(0.5)
#            return
#            
#        except Exception as e:
#            print(f"TTS Error (attempt {attempt + 1}): {e}")
#            try:
#                if nyapper:
#                    nyapper.stop()
#            except:
#                pass
#            nyapper = None
#            time.sleep(0.5)
#    
#    # If all attempts failed, just print
#    print(f"[TTS FAILED - Text only]: {text}")
#


load_dotenv() 

elevenlabs = ElevenLabs( api_key=os.getenv("ELEVENLABS_API_KEY"),)

def say_prompt(saying: str):
    print(saying)
    audio = elevenlabs.text_to_speech.convert(
    text= saying,
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128",
    )
    play(audio)



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
        print("Customer: ")
        name  = speakUp("")
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
        phone = speakUp("")
        prompt = f"""user said {phone} is their phone number please confirm that this is a valid phone number as in it seems like it is 10 numbers either words or numbers respond with 'valid phone number' else respond with 'invalid phone number'"""
        response = llm.invoke(prompt).content.lower()
        if response == "valid phone number":
            return phone
        else:
            print("invalid phone number")

#Tool function that will ask user for pick up or delivery
def pickUpOrDeliver(*args, **kwargs):
    while True:
        say_prompt("Would you like to pick up your order or have it delivered? ")
        user = speakUp("")
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
            say_prompt("Invalid choice. Please choose either 'pick up' or 'delivery'.")

def pickUplocation(*args, **kwargs):
    while True:

        say_prompt("Please provide your pick-up location: ")
        location = speakUp("")
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
            say_prompt("Invalid pick up location. Please try again.")

def deliverylocation(*args, **kwargs):
    while True:
        
        say_prompt("Please provide your delivery location: ")
        location = speakUp("")
        prompt = f"user said {location} is their delivery address if it looks like a real address respond with 'valid' else respond with 'invalid'"
        response = llm.invoke(prompt).content.lower()
        if response == "valid":
            return location
        else:
            say_prompt("Invalid address, please try again.") 

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

    say_prompt("Available menu items:")
    time.sleep(0.5) 
    for item, (price, desc) in menu.items():
        print(f"- {item}: ${price:.2f} - {desc}")

    say_prompt("What would you like to order? Feel free to ask questions about our menu items!")

    while True:
        user_input = speakUp("")

        # --------------------------
        # Step 1: Check if done
        # --------------------------
        done_prompt = f"""
        The user said: "{user_input}"

        Task:
        Determine if the user is indicating they are FINISHED ordering and want to proceed to checkout.

        Examples of "done":
        - "done"
        - "that's all"
        - "that's it"
        - "I'm finished"
        - "nothing else"
        - "that'll be all"
        - "just that"
        - "no more"
        - "finish my order"
        - "checkout"
        - "ready to order"
        - "complete my order"

        Examples of "not done":
        - "add another pizza"
        - "I want more"
        - "also get me..."
        - "what else do you have"
        - asking questions about menu items

        Respond with ONLY one word:
        - "done" if they're finished ordering
        - "continue" if they want to keep ordering or are asking questions

        Your entire response must be exactly: done OR continue
        """
        user_decision = llm.invoke(done_prompt).content.lower().strip()

        if user_decision == "done":
            if not order_items:
                say_prompt("Your order is empty! Please tell me what you'd like to order.")
                continue

            # Display current order
            print("\nYour current order:")
            for item, qty in order_items.items():
                price = menu[item][0] * qty
                speakUp(f"- {qty}x {item} (${price:.2f})")
            total = sum(menu[item][0] * qty for item, qty in order_items.items())
            speakUp(f"\nTotal: ${total:.2f}")

            confirm_input = speakUp("Is this correct? Say yes or no: ").lower().strip()

            confirm_prompt = f"""
            The user said: "{confirm_input}"

            Task:
            Determine if the user is CONFIRMING their order is correct or if they want to CHANGE it.

            Examples of "yes" (order is correct):
            - "yes"
            - "yeah"
            - "yep"
            - "correct"
            - "that's right"
            - "looks good"
            - "perfect"
            - "all good"
            - "affirmative"
            - "sure"
            - "ok"
            - "okay"

            Examples of "no" (wants to change order):
            - "no"
            - "nope"
            - "not quite"
            - "wait"
            - "hold on"
            - "change it"
            - "actually..."
            - "I want to modify"
            - "that's wrong"
            - "incorrect"

            Respond with ONLY one word:
            - "yes" if they're confirming the order is correct
            - "no" if they want to make changes

            Your entire response must be exactly: yes OR no
            """
            confirm = llm.invoke(confirm_prompt).content.lower().strip()
            if confirm == "yes":
                break
            else:
                say_prompt("Ok, let's continue with your order.")
                continue

        # --------------------------
        # Add user input to conversation
        # --------------------------
        conversation.append(f"User: {user_input}")

        # --------------------------
        # Step 2: Determine intent
        # --------------------------
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

        # --------------------------
        # Step 3: Handle menu questions
        # --------------------------
        if intent == "1":
            menu_prompt = (
                "You are a pizza expert. Answer the following customer question about our menu:,make it super short tho dont yap too too long lol limit yourself \n"
                f"Menu:\n{json.dumps(menu, indent=2)}\n\n"
                f"Customer question: {user_input}\n\n"
                "Provide a helpful, knowledgeable response focusing on ingredients, prices, and recommendations."
            )
            answer = llm.invoke(menu_prompt).content
            say_prompt(answer)
            continue

        # --------------------------
        # Step 4: Handle orders
        # --------------------------
        elif intent == "2":
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
                    # Validate items
                    invalid_items = []
                    for item, qty in parsed.items():
                        if item not in menu:
                            invalid_items.append(item)

                    if invalid_items:
                        suggestion_prompt = (
                            f"The customer asked for '{', '.join(invalid_items)}' but these aren't on our menu.\n"
                            f"Our menu items are: {', '.join(menu.keys())}\n"
                            "Suggest the closest menu item(s) that match what they want."
                        )
                        suggestion = llm.invoke(suggestion_prompt).content
                        say_prompt(suggestion)
                        continue

                    # Update order without overwriting previous items
                    for item, qty in parsed.items():
                        try:
                            qty_num = int(qty)
                            if qty_num >= 0:
                                order_items[item] = qty_num
                        except:
                            say_prompt(f"Invalid quantity for {item}")

                    if order_items:
                        say_prompt("Your updated order:")
                        for item, qty in order_items.items():
                            price = menu[item][0] * qty
                            print(f"- {qty}x {item} (${price:.2f})")
                        total = sum(menu[item][0] * qty for item, qty in order_items.items())
                        say_prompt(f"Total: ${total:.2f}")
                        say_prompt("What else would you like? Say 'done' to finish.")
                else:
                    clarification_prompt = (
                        f"The customer said: '{user_input}'\n"
                        "Generate a helpful response asking for clarification about their order.\n"
                        "Include an example of how they could phrase their order."
                    )
                    clarification = llm.invoke(clarification_prompt).content
                    say_prompt(clarification)

            except Exception as e:
                say_prompt("I apologize for the confusion. Could you please rephrase your order?")
                say_prompt("For example: 'I'd like 2 Pepperoni Pizzas' or 'one Margherita please'")

        # --------------------------
        # Step 5: Handle general chat
        # --------------------------
        else:
            chat_prompt = (
                "You are a friendly pizza restaurant assistant. Respond to the customer's message:\n"
                f"Customer: {user_input}\n\n"
                "Provide a friendly response and guide them toward making an order if appropriate."
            )
            response = llm.invoke(chat_prompt).content
            say_prompt(response)

    detailed_order = []
    for item, qty in order_items.items():
        if item in menu:
            price = menu[item][0]  
            detailed_order.append({
                "itemName": item,
                "quantity": qty,
                "price": price
            })

    return detailed_order

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

def firebasePusher(receipt_dict: dict):
    try:
        # If agent returned a Pydantic model, convert it to a plain dict first
        if hasattr(receipt_dict, "dict"):
            receipt_dict = receipt_dict.dict()

        # Normalize orderDetails (Pydantic models -> dict)
        if isinstance(receipt_dict.get("orderDetails"), list):
            normalized = []
            for item in receipt_dict["orderDetails"]:
                if hasattr(item, "dict"):
                    normalized.append(item.dict())
                elif isinstance(item, dict):
                    normalized.append(item)
                else:
                    # best-effort conversion
                    normalized.append({"itemName": str(item)})
            receipt_dict["orderDetails"] = normalized

        # RECALCULATE TOTAL PRICE FROM ORDER DETAILS
        total_price = 0.0
        if receipt_dict.get("orderDetails"):
            for item in receipt_dict["orderDetails"]:
                if isinstance(item, dict):
                    price = float(item.get("price", 0))
                    quantity = int(item.get("quantity", 0))
                    total_price += price * quantity
        
        # Update the totalPrice field with the calculated value
        receipt_dict["totalPrice"] = round(total_price, 2)
        
        print(f"[DEBUG] Calculated total price: ${total_price:.2f}")

        # Add timestamp in UTC ISO format if not present
        if not receipt_dict.get("timestamp"):
            receipt_dict["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Push under /orders
        new_ref = ref.child("orders").push(receipt_dict)
        print(f"Pushed receipt to Firebase at key: {new_ref.key}")
        print(f"Receipt data: {receipt_dict}")
        try:
            say_prompt("Order saved successfully. Thank you.")
        except Exception:
            pass
        return new_ref.key
    except Exception as exc:
        print(f"Failed to push receipt to Firebase: {exc}")
        return None

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

if __name__ == "__main__":
    try:
        say_prompt("Welcome to the Pizza Ordering System!")
    except Exception:
        print("Welcome to the Pizza Ordering System!")

    print("=" * 64)
    print("CUSTOMER SERVICE AGENT")
    print("=" * 64)

    conversation_history = [("user", "hi")]

    result = agent.invoke({"messages": conversation_history})
    firebasePusher(result["structured_response"])
    print(result["structured_response"])