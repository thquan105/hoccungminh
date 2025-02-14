import hashlib
import hmac
import json
import random
import requests
import urllib
import urllib.parse
import urllib.request
import google.generativeai as genai
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .vnpay import vnpay
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")


def home_view(request):
    return render(request, "home.html")

def hmacsha512(key, data):
    byteKey = key.encode("utf-8")
    byteData = data.encode("utf-8")
    return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()

@login_required
def payment_index(request):
    return render(request, "thq_payment/payment.html")

@login_required
def payment(request):
    if request.method == "POST":
        order_type = "billpayment"
        order_id = request.POST.get('order_id').strip()
        if not order_id:
            order_id = ''.join(random.choices("0123456789", k=9))
        amount = 25000
        order_desc = "Nâng cấp tài khoản"
        bank_code = "NCB"
        bank_code = request.POST.get('bank_code').strip()
        language = "vn"
        ipaddr = "192.168.1.1"
        # Build URL Payment
        vnp = vnpay()
        vnp.requestData["vnp_Version"] = "2.1.0"
        vnp.requestData["vnp_Command"] = "pay"
        vnp.requestData["vnp_TmnCode"] = settings.VNPAY_TMN_CODE
        vnp.requestData["vnp_Amount"] = amount * 100
        vnp.requestData["vnp_CurrCode"] = "VND"
        vnp.requestData["vnp_TxnRef"] = order_id
        vnp.requestData["vnp_OrderInfo"] = order_desc
        vnp.requestData["vnp_OrderType"] = order_type
        # Check language, default: vn
        if language and language != "":
            vnp.requestData["vnp_Locale"] = language
        else:
            vnp.requestData["vnp_Locale"] = "vn"
            # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
        if bank_code and bank_code != "":
            vnp.requestData["vnp_BankCode"] = bank_code

        vnp.requestData["vnp_CreateDate"] = datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )  # 20150410063022
        vnp.requestData["vnp_IpAddr"] = ipaddr
        vnp.requestData["vnp_ReturnUrl"] = settings.VNPAY_RETURN_URL
        vnpay_payment_url = vnp.get_payment_url(
            settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY
        )
        print(vnpay_payment_url)
        return redirect(vnpay_payment_url)
    else:
        messages.warning(request, "Lỗi phương thức")
        return render(request, "home.html")

@login_required
def payment_return(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData["vnp_TxnRef"]
        amount = int(inputData["vnp_Amount"]) / 100
        order_desc = inputData["vnp_OrderInfo"]
        vnp_TransactionNo = inputData["vnp_TransactionNo"]
        vnp_ResponseCode = inputData["vnp_ResponseCode"]
        vnp_TmnCode = inputData["vnp_TmnCode"]
        vnp_PayDate = inputData["vnp_PayDate"]
        vnp_BankCode = inputData["vnp_BankCode"]
        vnp_CardType = inputData["vnp_CardType"]
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            if vnp_ResponseCode == "00":
                profile = request.user.profile
                profile.is_premium = True
                profile.save()
                return render(
                    request,
                    "thq_payment/payment_return.html",
                    {
                        "title": "Kết quả thanh toán",
                        "result": "Thành công",
                        "order_id": order_id,
                        "amount": amount,
                        "order_desc": order_desc,
                        "vnp_TransactionNo": vnp_TransactionNo,
                        "vnp_ResponseCode": vnp_ResponseCode,
                    },
                )
            else:
                return render(
                    request,
                    "thq_payment/payment_return.html",
                    {
                        "title": "Kết quả thanh toán",
                        "result": "Lỗi",
                        "order_id": order_id,
                        "amount": amount,
                        "order_desc": order_desc,
                        "vnp_TransactionNo": vnp_TransactionNo,
                        "vnp_ResponseCode": vnp_ResponseCode,
                    },
                )
        else:
            return render(
                request,
                "thq_payment/payment_return.html",
                {
                    "title": "Kết quả thanh toán",
                    "result": "Lỗi",
                    "order_id": order_id,
                    "amount": amount,
                    "order_desc": order_desc,
                    "vnp_TransactionNo": vnp_TransactionNo,
                    "vnp_ResponseCode": vnp_ResponseCode,
                    "msg": "Sai checksum",
                },
            )
    else:
        return render(
            request,
            "thq_payment/payment_return.html",
            {"title": "Kết quả thanh toán", "result": ""},
        )

@login_required
def writing_view(request):
    nguoi_dung = request.user
    profile = nguoi_dung.profile

    if not profile.is_premium:
        messages.warning(request, "Vui lòng nâng cấp tài khoản để sử dụng tính năng này.")
        return redirect("home")
    return render(request, "thq_writing/writing_index.html")

def prompt_1(text):
    return f"""Generate a JSON structure for paragraphs in this given text: "{text}" exactly like this:
        {{
          "request": [
            {{
              "original_Paragraph": "Place the original paragraph from the text here.",
              "corrected_Paragraph": "Provide the corrected version after analyzing grammar, collocation, or conceptual issues (add linking words if needed to make the paragraph cohesive). If the original paragraph is correct, this field should replicate the original paragraph. Use the same CSS class to highlight updated words/ phrases, like <span class='highlight-vocab'>...</span>",
              "explain_Correction": "State type of error and provide a detailed explanation for each corrected word/ phrase in Vietnamese (using Cambridge dictionary and grammar as references). If there is nothing to correct, return 'No issue was found'. Use the same CSS class to highlight updated words/ phrases, like <span class='highlight-vocab'>...</span>"
            }}
          ]
        }},
        
        Sample:
        {{
          "request": [
            {{
              "original_Paragraph": "Owning a mobile phone can help old people easily contact their relatives. Old people who live alone can feel lonely and isolated.",
              "corrected_Paragraph": "Owning <span class='highlight-vocab'>a</span> mobile phone can help old people <span class='highlight-vocab'>to</span> easily contact their relatives.",
              "explain_Correction": "Lỗi ngữ pháp: 'help young people easily contact' sửa thành <span class='highlight-vocab'>‘help young people to easily contact’</span> (Thêm 'to' trước động từ nguyên thể để phù hợp với cấu trúc 'help someone to do something'). 
              Ý tưởng thiếu logic: 'Old people who live alone can feel lonely and isolated' sửa thành <span class='highlight-vocab'>‘As a result, those who live alone would feel less lonely and isolated’</span> (Việc sử dụng điện thoại liên lạc sẽ giúp người già bớt cô đơn, không phải khiến họ cô đơn. Old people sửa thành those để tránh lặp từ)."
            }}
          ]
        }},

        Ensure all paragraphs from the given text are included in the JSON structure, following this template. The aim is to facilitate a comprehensive analysis and enhancement of the text, making it more engaging and understandable to a wider audience."""

@login_required
def writing_evaluate(request):
    if request.method == "POST":
        text = request.POST.get("inputText").strip()

        inputUser = prompt_1(text)
        inputUser2 = f"""Generate a JSON structure for the given English paragraph: {text}"""

        dt_response = {}
        dt_response_2 = {}

        prompt = """
            *output:
            {
                "original_Paragraph": "Place the original paragraph (multiple sentences) from the text here.",
                "taskResponse": {
                    "score": "0-9",
                    "feedback": "Evaluate the paragraph based on the following criteria (use Vietnamese for feedback):\n
                        1. Relevance to the topic: Evaluate if the paragraph stays on topic and responds directly to the prompt.\n
                        2. Addressing all parts of the task: Ensure that all aspects of the task are covered adequately.\n
                        3. Providing a clear position or purpose: Look for a well-defined thesis or argument.\n
                        4. Minimum word count: Ensure the paragraph meets the required word count of at least 250 words (essay) or 150 words (report).",
                    "errors": "List any issues related to task response, focusing on missed points or unclear arguments. Provide feedback in Vietnamese.",
                    "exampleImprovements": "Generate **multiple** detailed suggestions for improving the task response (use Vietnamese). Focus on clarity, depth, and covering all aspects of the task, and examples use English."
                },
                "coherence": {
                    "score": "0-9",
                    "feedback": "Evaluate coherence based on:\n
                        1. Logical flow of ideas: Assess the organization and logical structure of the paragraph.\n
                        2. Use of cohesive devices: Review the use of linking words, pronouns, and other cohesive elements to ensure smooth transitions.",
                    "errors": "List all issues related to coherence, such as abrupt shifts in ideas or lack of logical progression (use Vietnamese).",
                    "exampleImprovements": "Generate **multiple** examples to enhance coherence, focusing on improving transitions and logical flow (use Vietnamese). Provide English examples for better clarity, and examples use English."
                },
                "vocabulary": {
                    "score": "0-9",
                    "feedback": "Evaluate vocabulary based on:\n
                        1. Range of vocabulary: Check if the paragraph uses a variety of vocabulary.\n
                        2. Use of less common vocabulary: Ensure that more advanced or less frequent words are used appropriately.\n
                        3. Correct word usage: Review for proper and contextually accurate word choices.\n
                        4. Spelling accuracy: Verify that spelling is correct throughout the paragraph.",
                    "errors": "List any vocabulary-related issues, such as incorrect word usage, repetition, or spelling mistakes (use Vietnamese).",
                    "exampleImprovements": "Generate **multiple** examples for improving vocabulary, including the use of synonyms and more precise language (use Vietnamese). Provide English examples for clarity, and examples use English."
                },
                "grammar": {
                    "score": "0-9",
                    "feedback": "Evaluate grammar based on:\n
                        1. Range of grammatical structures: Check for variety in sentence types and structures.\n
                        2. Accuracy of grammatical structures: Ensure proper use of grammar, including tenses, articles, and prepositions.\n
                        3. Punctuation: Review correct punctuation usage for clarity.",
                    "errors": "List any grammar issues, such as incorrect tense usage, missing punctuation, or awkward sentence structure (use Vietnamese).",
                    "exampleImprovements": "Generate **multiple** examples to improve grammar, focusing on sentence structure, verb tense, and punctuation (use Vietnamese). Provide English examples for better understanding, and examples use English"
                }
            }
        """
        try:
            genai.configure(api_key=API_KEY)

            generation_config = {
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 20000,
                "response_mime_type": "application/json",
            }

            model = genai.GenerativeModel(
                model_name=MODEL_NAME,
                generation_config=generation_config,
            )

            model_2 = genai.GenerativeModel(
                model_name=MODEL_NAME,
                system_instruction=prompt,
                generation_config=generation_config,
            )

            test_response = model.generate_content(inputUser)
            test_response_2 = model_2.generate_content(inputUser2)

            data_response = test_response.text
            data_response_2 = test_response_2.text
            try:
                dt_response = json.loads(data_response)
                dt_response_2 = json.loads(data_response_2)
            except:
                print("Invalid JSON response from API.")

        except requests.RequestException as e:
            print(f"Error in API request: {str(e)}")
        if not dt_response and not dt_response_2:
            messages.warning(
                request,
                "Không thể tạo câu hỏi từ nội dung đã cung cấp. Vui lòng thử lại.",
            )
            return redirect("writing_index")
        average_score = 0
        if dt_response_2:
            task_score = float(dt_response_2.get('taskResponse', {}).get('score', 0))
            coherence_score = float(dt_response_2.get('coherence', {}).get('score', 0))
            vocabulary_score = float(dt_response_2.get('vocabulary', {}).get('score', 0))
            grammar_score = float(dt_response_2.get('grammar', {}).get('score', 0))

            average = (task_score + coherence_score + vocabulary_score + grammar_score) / 4
            average_score = round(average, 2)

        return render(
            request,
            "thq_writing/writing_result.html",
            {
                "data": dt_response,
                "data_2": dt_response_2,
                "dtb": average_score,
            },
        )
    else:
        messages.warning(request, "Lỗi phương thức")
        return redirect("writing_index")
