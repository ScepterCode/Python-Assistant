import google.generativeai as genai

genai.configure(api_key="AIzaSyAKbqKUZvxYbrAgY0gwRX_dqUq7z2AP5Uw")

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(model.name)