import re


def extract_session(session_str: str):
    match = re.search(r"/sessions/(.*?)/contexts/", session_str)
    if match:
        extracted_string = match.group(1)
        return  extracted_string
    return "no match"

def get_str_from_food_dict(food_dict: dict):
    return ", ".join([f"{int(value)} {key}" for key, value in food_dict.items()])

if __name__ == "__main__":
    print(get_str_from_food_dict({"pizza": 1, "lassi": 3}))
    # print(extract_session("projects/newagent-nydn/agent/sessions/03835bb8-6dcf-531f-f0a3-99ddf736e81f/contexts/ongoing-order"))