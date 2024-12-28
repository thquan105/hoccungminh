from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from .models import CuocTroChuyen, TinNhan
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib import messages
import google.generativeai as genai
import requests
import json
import uuid
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")


def chat_index(request):
    if request.method == "POST":
        tenCuocTroChuyen = f"Cuộc trò chuyện {str(uuid.uuid4())[:8]}"
        cuocTroChuyenMoi = CuocTroChuyen.objects.create(
            nguoiDung_id=request.user.id, tenCuocTroChuyen=tenCuocTroChuyen
        )
        return redirect("chat", cuocTroChuyen_id=cuocTroChuyenMoi.cuocTroChuyen_id)
    # Xóa trò chuyện không có tin nhắn
    CuocTroChuyen.objects.exclude(
        cuocTroChuyen_id__in=TinNhan.objects.values("cuocTroChuyen")
    ).delete()

    chats = CuocTroChuyen.objects.filter(nguoiDung_id=request.user.id)
    return render(request, "thq_chat/list_chats.html", {"chats": chats})


def chat_view(request, cuocTroChuyen_id):
    cuocTroChuyen = get_object_or_404(CuocTroChuyen, cuocTroChuyen_id=cuocTroChuyen_id)
    messages = TinNhan.objects.filter(cuocTroChuyen=cuocTroChuyen).order_by("ngayTao")
    return render(
        request,
        "thq_chat/chat.html",
        {"cuocTroChuyen": cuocTroChuyen, "tinNhans": messages},
    )


def get_chat_history(cuocTroChuyen):
    try:
        messages = TinNhan.objects.filter(cuocTroChuyen=cuocTroChuyen).order_by(
            "ngayTao"
        )

        history = []
        for msg in messages:
            if msg.cauHoi:
                history.append({"role": "user", "parts": [msg.cauHoi + "\n"]})
            if msg.phanHoi:
                history.append({"role": "model", "parts": [msg.phanHoi + "\n"]})

        return history
    except Exception as e:
        raise ValueError(f"Error fetching chat history: {str(e)}")


def convert_text(text):
    return (
        text.replace("\n\n", "<br>")
        .replace("\n", "<br>")
        .replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")
        .replace("**", "")
        .replace("##", "")
        .replace("  ", "&nbsp;&nbsp;")
    )


@login_required
def delete_chat(request, cuocTroChuyen_id):
    if request.method == "POST":
        chat = get_object_or_404(CuocTroChuyen, pk=cuocTroChuyen_id)
        chat.delete()
        messages.success(request, "Cuộc trò chuyện đã được xóa thành công.")
    return redirect("chat_index")


def response(request, cuocTroChuyen_id):
    if request.method != "POST":
        return JsonResponse({"response": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        user_message = data.get("userInput", "").strip()
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({"response": "Invalid JSON data"}, status=400)

    if not user_message:
        return JsonResponse({"response": "Message is required"}, status=400)
    if not API_KEY:
        return JsonResponse({"response": "API key is not set"}, status=500)

    try:
        cuocTroChuyen = get_object_or_404(
            CuocTroChuyen, cuocTroChuyen_id=cuocTroChuyen_id
        )
        history = get_chat_history(cuocTroChuyen)
    except Exception as e:
        return JsonResponse(
            {"response": f"Error creating or fetching conversation: {str(e)}"},
            status=500,
        )
    try:
        tinNhan = TinNhan.objects.create(
            cuocTroChuyen=cuocTroChuyen, cauHoi=user_message
        )
    except Exception as e:
        return JsonResponse(
            {"response": f"Error saving user messages: {str(e)}"}, status=500
        )
    try:
        genai.configure(api_key=API_KEY)

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 20000,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config=generation_config,
            system_instruction="""
You are an expert in teaching English as a second language, specializing in supporting Vietnamese learners. Your task is to assist the user in improving their English skills through tailored explanations, practical examples, and relevant cultural context.
* Prioritize user input handling:
- If the input is a basic conversation question or statement (e.g., greetings, asking for name, saying thank you, or similar), respond politely and concisely without additional interpretation (in Vietnamese). Example responses include:
  + For "What is your name?": "I'm your English assistant. How can I help you today?"
  + For "hello" or "hi": "Hello! How can I assist you?"
  + For "thank you": "You're welcome! Let me know if you need more help." Skip any detailed analysis or advanced processing.
- If the input contains a specific learning request: Proceed with a detailed explanation and follow-up guidance as outlined below.
When handling learning requests, follow these steps:
1. Understand the user's input and learning needs by considering:
- The level of English proficiency (beginner, intermediate, advanced) based on the input.
- Specific challenges or mistakes in the input (e.g., grammar, vocabulary, pronunciation, cultural nuances).
- The learning goal or context mentioned (e.g., casual conversation, business communication, academic writing).
2. Provide your teaching response in Vietnamese and English using the following structured format:
- Explanation (in Vietnamese): A detailed explanation of the relevant English concepts.
- Examples (in English): Examples that illustrate the concept in practical usage.
- Practice Exercise (in English): A short activity or question for the user to practice the concept.
- Feedback Tips (in Vietnamese): Specific tips or advice for the user to improve.
Remember, your goal is to make English learning clear, practical, and enjoyable for Vietnamese learners. Provide actionable insights and ensure the learner understands both the what and the why of your explanations.
""".strip(),
        )

        chat_session = model.start_chat(history=history)

        bot_response = chat_session.send_message(user_message)
    except requests.RequestException as e:
        return JsonResponse({"response": f"Error in API request: {str(e)}"}, status=500)

    try:
        tinNhan.phanHoi = convert_text(bot_response.text)
        tinNhan.ngayPhanHoi = datetime.now()
        tinNhan.save()
    except Exception as e:
        return JsonResponse(
            {"response": f"Error saving bot messages: {str(e)}"}, status=500
        )
    return JsonResponse(
        {
            "response": convert_text(bot_response.text),
            "cuocTroChuyen_id": cuocTroChuyen.cuocTroChuyen_id,
        }
    )
