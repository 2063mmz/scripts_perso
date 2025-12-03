import requests
from typing import Optional, Dict
import re
import json
import random
import gradio as gr

# Defined a list of keywords that users might use and corresponding response templates.

begin = ["hi", "hello", "hey", "sup", "salut","nice to meet you"]
question = ["how are", "are you", "and you"]
answer_pos = ["yes", "wow","haha","happy","good", "i'm ok", "great", "not bad", "like", "lovely", "love"]
answer_neg = ["no", "not ok", "bad", "sad", "terrible", "horrendous", "cry", "hate"]

reply_begin = [
    "{text}! I'm your AI agent!",
    "{text}! How can I help you?",
    "{text}! Wanna chat with me?",
    "{text}! How are you today?"
]

reply_question = [
    "As your AI agent, I'm great, thanks.",
    "Thank you for asking me, I feel so fresh!"
]

reply_answer_pos = [
    "Glad to hear that!",
    "WOW!",
    "I'm so happy for you!",
    "Haha"
]

reply_answer_neg = [
    "Awww, sorry to hear that. Wanna a joke to cheer you up?",
    "I feel sad when you say that.",
    ":< Cheer up!"
]

reply_cue_calcul = ["Do you wanna calculate some numbers?"]

reply_cue_dog = [
    "Do you love puppies?", 
    "Do you wanna see some lovely puppy pictures?"
]

reply_cue_jock = [
    "Wanna a laugh?", 
    "I can tell you a joke, wanna hear it?"
]

reply_cue_tlou = [
    "Hey, wanna play a little test game with me?",
    "Do you wanna know which character you are in The Last of Us?"
]

# Mapping of tool/function names to their corresponding cue responses for guiding the user into using one of the available tools
cue_tool = {
    "calcul": reply_cue_calcul,
    "get_random_dog_image": reply_cue_dog,
    "get_random_joke": reply_cue_jock,
    "guess_tlou_character": reply_cue_tlou
}

## == Fuction1: Calcul == ##

def calcul(num1: float, num2: float, fonction: str) -> str:
    if fonction == '+':
        result = num1 + num2
        return (f'{num1} + {num2} = {result}')
    elif fonction == '-':
        result = num1 - num2
        return(f'{num1} - {num2} = {result}')
    elif fonction == '*':
        result = num1 * num2
        return(f'{num1} * {num2} = {result}')
    elif fonction == '/':
        if num2 == 0:
            # If dividing by zero, return an error message
            return 'num2 can not be 0'
        else:
            result = num1 / num2
            return(f'{num1} / {num2} = {result}')
        
def parse_calc(text: str) -> tuple[float, float, str]:
    nums = list(map(float, re.findall(r'-?\d+(?:\.\d+)?', text)))
    if len(nums) < 2:
        raise ValueError("Need two numbers")
    a, b = nums[0], nums[1]
    low = text.lower()
    if any(x in low for x in ["plus", "+", "add"]):
        op = "+"
    elif any(x in low for x in ["minus", "-", "subtract"]):
        op = "-"
    elif any(x in low for x in ["multiply", "*", "times"]):
        op = "*"
    elif any(x in low for x in ["divide", "/"]):
        op = "/"
    else:
        op = "+"
    return a, b, op


## == Fuction2: get random dog image == ##

def get_random_dog_image() -> str:
    # Send a .get request to get a random dog image
    resp = requests.get("https://dog.ceo/api/breeds/image/random")
    data = resp.json()
    if data.get("status") == "success":
        # Return to the image url
        return data["message"]
    else:
        raise ValueError(f"Request failed:{data}")
    
## == Fuction3: get random joke == ##

def get_random_joke() -> str:
    url = "https://official-joke-api.appspot.com/random_joke"
    resp = requests.get(url)
    resp.raise_for_status()
    data: Dict = resp.json()
    # Data example：{"id":161,"type":"general","setup":"...","punchline":"..."}
    setup = data.get("setup", "")
    punchline = data.get("punchline", "")
    return f"{setup}\n— {punchline}"

## == Fuction4: TLOU quiz == ##

def guess_tlou_character(answers_raw: str) -> str:
    scores = {
        "Ellie": 0,
        "Joel": 0,
        "Abby": 0
    }

    choices = [c.upper() for c in answers_raw if c.upper() in ["A", "B", "C"]]
    if len(choices) < 5:
        return (
            "Please reply with at least 5 choices using A/B/C, e.g. 'A B C A B'."
        )

    q_maps = [
        {"A": "Joel",  "B": "Abby",  "C": "Ellie"},  # Q1
        {"A": "Ellie", "B": "Joel",  "C": "Abby"},   # Q2
        {"A": "Ellie", "B": "Joel",  "C": "Abby"},   # Q3
        {"A": "Abby",  "B": "Ellie", "C": "Joel"},   # Q4
        {"A": "Joel",  "B": "Abby",  "C": "Ellie"},  # Q5
    ]

    for i, choice in enumerate(choices[:5]):
        char = q_maps[i][choice]
        scores[char] += 1

    max_score = max(scores.values())
    top_characters = [char for char, score in scores.items() if score == max_score]

    character_links = {
        "Joel": "https://thelastofus.fandom.com/wiki/Joel_Miller",
        "Ellie": "https://thelastofus.fandom.com/wiki/Ellie",
        "Abby": "https://thelastofus.fandom.com/wiki/Abby_Anderson"
    }

    result = random.choice(top_characters)
    link = character_links.get(result, "")
    
    return (
        f"Yeah!🎉 You are most like ᖭ༏ᖫ {result} ཐི༏ཋྀ from The Last of Us!🥳\n"
        f"Learn more about {result}: {link}"
    )

# Simulates an AI agent's response to user input
def llm_simulater(user_input: str, confirm: str, sub_input: str) -> Dict:
    # Convert input to lowercase
    user = user_input.lower() 
    
    # Randomly prepare a cue for fallback
    tool, templates = random.choice(list(cue_tool.items()))
    reply_cue = random.choice(templates)

    # Small Talk
    if any(word in user for word in begin):
        reply = random.choice(reply_begin).format(text=user)
        return json.dumps({
            "action": "begin_chat", 
            "args": {"reply":reply}
        })
    
    if any(word in user for word in question):
        reply = random.choice(reply_question)
        return json.dumps({
            "action": "question", 
            "args": {"reply": reply}
        })
    
    # Sentiment, positive or negative
    if any(word in user for word in answer_pos):
        reply = random.choice(reply_answer_pos)
        return json.dumps({
            "action": "answer_pos", 
            "args": {"reply": reply}
        })

    if any(word in user for word in answer_neg):
        reply = random.choice(reply_answer_neg)
        return json.dumps({
            "action": "answer_neg", 
            "args": {"reply": reply}
        })
    
    # Tool: Calculator
    if any(op in user for op in ["add", "calcul", "plus", "+", "subtract", "minus", "-", "multiply", "*", "divide", "/"]):
        if confirm.lower() not in ["yes","y"]:
            return json.dumps({
                "action": "cue_tool", 
                "args": {
                    "tool" : tool,
                    "reply": reply_cue}
            })
        
        try:
            a, b, op = parse_calc(sub_input)
        except ValueError:
            return json.dumps({
                "action": "cue_tool", 
                "args": {
                    "tool" : tool,
                    "reply": reply_cue}
            })
        
        else:
            return json.dumps({
                "action": "calcul",
                "args": {"num1": a, "num2": b, "fonction": op}
            })


    # Tool: Dog Picture
    if any(word in user_input for word in ["puppy", "doggy", "dogs", "dog", "pictures", "picture", "images"]):
        if confirm.lower() not in ["yes","y"]:
            return json.dumps({
                "action": "cue_tool", 
                "args": {
                    "tool" : tool,
                    "reply": reply_cue}
            })
        else:
            return json.dumps({
                "action": "get_random_dog_image",
                "args": {}
            })
        
    # Tool: Joke
    if any(word in user_input for word in ["jokes","joke","laugh","story"]):
        if confirm.lower() not in ["yes","y"]:
            return json.dumps({
                "action": "cue_tool", 
                "args": {
                    "tool" : tool,
                    "reply": reply_cue}
            })
        else:
            return json.dumps({
                "action": "get_random_joke",
                "args": {}
            })
        
    # Tool: The Last of Us test
    if any(word in user_input for word in ["guess","game","the last of us","series","naughty dog","pedro","test","character","character"]):
        if confirm.lower() not in ["yes","y"]:
            return json.dumps({
                "action": "cue_tool", 
                "args": {
                    "tool" : tool,
                    "reply": reply_cue}
            })
        else:
            return json.dumps({
                "action": "guess_tlou_character",
                "args": {}
            })
    
    # Fallback response
    else:
        return json.dumps({
            "action": "cue_tool", 
            "args": {
                "tool" : tool,
                "reply": reply_cue}
        })
    
def agent_response(user_input: str, pending_tool: Optional[str], chat_count: int, reject_count: int) -> tuple[str, Optional[str], int]:
    user = user_input.strip().lower()
    image_url: Optional[str] = None
    # pending tool flow
    if pending_tool:
        if user in ["yes","y"]:
            reject_count = 0
            if pending_tool == "calcul":
                return ("🧙‍♀️ Please enter calculation like '8 plus 2'", pending_tool, chat_count, reject_count)
            if pending_tool == "get_random_dog_image":
                image_url = get_random_dog_image()
                return ("", image_url, None, chat_count, reject_count)
            if pending_tool == "get_random_joke":
                return (f"🧙‍♀️ {get_random_joke()}", None, None, chat_count,reject_count)
            if pending_tool == "guess_tlou_character":
                questions_text = (
                "Let's do a quick TLOU character quiz.\n"
                "Reply with 5 letters (A/B/C), e.g. 'A B C A B'.\n\n"
                "1. Which thought scares you the most?\n"
                "   A. Failing to protect the ones I love.\n"
                "   B. Becoming the kind of person I hate.\n"
                "   C. Ending up alone, with no one left to trust.\n\n"
                "2. What drives you to keep going?\n"
                "   A. Books, songs, and memories.\n"
                "   B. Duty. I made a promise. I’ll keep it.\n"
                "   C. Justice. I must finish what I started.\n\n"
                "3. In a group, you're usually the:\n"
                "   A. Bold explorer with strong instincts.\n"
                "   B. Reliable backbone who keeps things together.\n"
                "   C. Action-first doer who leads from the front.\n\n"
                "4. What’s your biggest regret?\n"
                "   A. Letting revenge consume me.\n"
                "   B. Hurting someone I didn’t mean to.\n"
                "   C. Failing to protect someone I love.\n\n"
                "5. When facing the loss of a loved one or friend, you:\n"
                "   A. Close off emotionally, but hold onto memories.\n"
                "   B. Look for allies and solve it together.\n"
                "   C. Try to stay connected to what’s left.\n"
                )
                return (f"🧙‍♀️ {questions_text}", None, "guess_tlou_character_run", chat_count, reject_count)

        if user in ["no","n"]:
                reject_count += 1
                if reject_count >= 3:
                    # after three rejects, back to chat
                    return ("🧙‍♀️ Okay, let's just chat then! What would you like to talk about?", None, chat_count, 0)
                t, tmpls = random.choice(list(cue_tool.items()))
                return (f"🧙‍♀️ {random.choice(tmpls)} (yes/no)", None, t, chat_count, reject_count)
        else:    
            return ("🧙‍♀️ Please answer yes or no.", pending_tool, chat_count,reject_count)
    # at the TLoU mood
    if pending_tool == "guess_tlou_character_run":
        result = guess_tlou_character(user_input)
        return (f"🧙‍♀️ {result}", None, None, chat_count, reject_count)
    
    # direct calculation
    if any(op in user for op in ["plus","+","minus","-","*","times","/","divide"]):
        nums = re.findall(r'-?\d+(?:\.\d+)?', user)
        if len(nums) >= 2:
            a, b = float(nums[0]), float(nums[1])
            if any(x in user for x in ["+","plus"]): op = "+"
            elif any(x in user for x in ["-","minus"]): op = "-"
            elif any(x in user for x in ["*","times"]): op = "*"
            else: op = "/"
            return (f"🧙‍♀️ {calcul(a, b, op)}", None, None, chat_count, reject_count)
        return ("🧙‍♀️ I couldn't parse calculation. Try '5 times 6'", "", None, chat_count, reject_count)
    
    # LLM simulate and chat count
    raw = llm_simulater(user_input, '', '')
    try:
        block = json.loads(raw)
    except json.JSONDecodeError:
        return ("🧙‍♀️ Sorry, I didn't understand.", "", chat_count)
    action = block.get("action")
    args = block.get("args", {})
    
    # chat actions
    if action in ["begin_chat","question","answer_pos","answer_neg"]:
        chat_count += 1
        if chat_count > 3:
            t, tmpls = random.choice(list(cue_tool.items()))
            reply = random.choice(tmpls)
            return (f"🧙‍♀️ Let's talk about something else!\n{reply} (yes/no)", t, 0, reject_count)
        return (f"🧙‍♀️ {args.get('reply','')}" , None, None, chat_count, reject_count)
    if action == "cue_tool":
        return (f"🧙‍♀️ {args.get('reply','')} (yes/no)", None, args.get("tool"), chat_count, reject_count)

    # tool actions
    if action == "calcul":
        return (f"🧙‍♀️ {calcul(**args)}", None, None, chat_count)
    if action == "get_random_dog_image":
        url = get_random_dog_image()
        return ("", image_url, None, chat_count, reject_count)
    if action == "get_random_joke":
        return (f"🧙‍♀️ {get_random_joke()}", None, None, chat_count)
    if action == "guess_tlou_character":
        questions_text = (
        "Let's do a quick TLOU character quiz.\n"
        "Reply with 5 letters (A/B/C), e.g. 'A B C A B'.\n"
        "(I'll ask questions in the next message.)"
        )
        return (f"🧙‍♀️ {questions_text}", None, "guess_tlou_character_run", chat_count, reject_count)

    else:
        return ("🧙‍♀️ Sorry, I didn't understand.", "", None, chat_count)

## == Gradio UI == ##
def build_agent_ui():
    with gr.Blocks() as demo:
        gr.Markdown("## 🧙‍♀️ AI Agent")
        msg = gr.Textbox(label="👤 User", placeholder="Say something...", lines=1)
        txt_out = gr.Textbox(label="🧙‍♀️ AI Agent", lines=2)
        html_out = gr.HTML(label="AI Agent Image")

        pending_tool = gr.State(value=None)
        chat_count = gr.State(value=0)
        reject_count = gr.State(value=0)

        msg.submit(
            fn=agent_response,
            inputs=[msg, pending_tool, chat_count, reject_count],
            outputs=[txt_out, html_out, pending_tool, chat_count, reject_count]
        
        )
    return demo

if __name__ == "__main__":
    demo = build_agent_ui()
    demo.launch()