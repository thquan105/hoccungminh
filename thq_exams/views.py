from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Count, Avg, Max, F
from .models import DeThi, CauHoi, LuaChon, KetQua
from django.contrib.auth.decorators import login_required
from urllib.parse import parse_qs
from .utils import check_and_reset_luot_tao
import google.generativeai as genai
import requests
import json
import uuid
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

@login_required
def test_index(request):
    deThis = DeThi.objects.filter(trangThai=True).order_by("-ngayTao")
    ket_quas = (
        KetQua.objects.filter(loai=True)
        .values("nguoiDung__username")
        .annotate(so_cau=Count("deThi__cau_hoi"), diem_tb=Avg("diemSo"))
        .order_by("-diem_tb", "so_cau")
    )

    xep_hang = []
    for ket_qua in ket_quas[:10]:
        nguoi_dung = ket_qua["nguoiDung__username"]
        so_cau = ket_qua["so_cau"]
        diem_tb = ket_qua["diem_tb"]

        xep_hang.append(
            {
                "nguoi_dung": nguoi_dung,
                "so_cau": so_cau,
                "diem_tb": diem_tb,
            }
        )
    return render(
        request, "thq_exams/index.html", {"deThis": deThis, "xep_hang": xep_hang}
    )


@login_required
def practice_index(request):
    user = request.user
    profile = user.profile
    check_and_reset_luot_tao(profile)
    deThis = DeThi.objects.filter(nguoiTao=user).order_by("-ngayTao")
    luotConLai = profile.daily_question_limit - profile.created_questions_today
    return render(
        request,
        "thq_exams/practice_index.html",
        {"deThis": deThis, "luotConLai": luotConLai},
    )


@login_required
def delete_practice(request, deThi_id):
    if request.method == "POST":
        deThi = get_object_or_404(DeThi, deThi_id=deThi_id)
        deThi.delete()
        messages.success(request, "Đề Thi đã được xóa thành công.")
    return redirect("practice_index")


def save_question(json_data, user=None):
    try:
        deThi = DeThi.objects.create(
            tenDeThi=json_data.get("exam_name", f"Đề thi {str(uuid.uuid4())[:5]}"),
            thoiGian=20,
            moTa=json_data.get("moTa", ""),
            nguoiTao=user,
            doanVan=json_data.get("reading_passage", ""),
        )

        questions_to_create = []

        for question in json_data.get("questions", []):
            options = question.get("options", [])
            correct_answer = question.get("correct_answer", "").upper()

            if correct_answer not in ["A", "B", "C", "D"]:
                raise ValueError(f"Invalid correct answer: {correct_answer}")

            questions_to_create.append(
                CauHoi(
                    deThi=deThi,
                    noiDung=question.get("question", ""),
                    dapAnA=options[0] if len(options) > 0 else "",
                    dapAnB=options[1] if len(options) > 1 else "",
                    dapAnC=options[2] if len(options) > 2 else "",
                    dapAnD=options[3] if len(options) > 3 else "",
                    dapAnDung=correct_answer,
                    giaiThich=question.get("explanation", ""),
                )
            )

        CauHoi.objects.bulk_create(questions_to_create)

        deThi.thoiGian = len(questions_to_create) * 2 + 5
        deThi.save()

    except Exception as e:
        raise Exception(f"Error saving data: {str(e)}")

    return deThi


def prompt_to_test(typeQs, numQs, contentQs):
    typeQuestion = typeQs == "1"
    questionType = "reading comprehension" if typeQuestion else "multiple-choice"
    reading_passage = require = ""
    if typeQuestion:
        reading_passage = '"reading_passage": "... (Optional reading passage, A passage containing more than 3 paragraphs and at 750 words, if required)",'
        require = "- question content: based on the passage"

    prompt = f"""
    *instruction: Generate multiple-choice questions based on the provided content. The input content can be in English or Vietnamese. Tailor the questions to match the context and difficulty specified. All questions must be in English, and explanations for correct answers must be in Vietnamese.
    *requests: 
    - input content: The content or text to generate multiple-choice questions from. The input can be in English or Vietnamese.
    - number of questions: {numQs}
    - question format: {questionType}
    - goal: Help learners improve their English skills, understand grammar, vocabulary.
    - language: English
    *requirements:
    - difficulty: medium
    {require}
    - purpose of explanation: make English learning clear, practical, and enjoyable for Vietnamese learners
    - answer_count: 4            
    *output:
    {{ 
        "exam_name": "... (Generate a name for the exam (maximum 10 words) based on the provided content in Vietnamese)",
        {reading_passage}
        "questions": [
            {{
                "question": "... (The generated multiple-choice question in English)",
                "options": ["(Option A)","(Option B)","(Option C)","(Option D)"],
                "correct_answer": "... (The correct option, e.g., 'A')",
                "explanation": "... (Explanation in Vietnamese with direct references or examples from the passage in English)"
            }}
            ...
        ] 
    }}"""
    inputUser = f"""Generate multiple-choice questions in detail based on the following format. Use the content ({contentQs}) and specifications to create contextually accurate questions.
    - If the title is not enough to create a question, you can add the necessary context and content to create the question yourself.
    - If there is an error, the response is "I couldn't find information about your request."
    All questions must be in English, and explanations for correct answers with direct references or examples to aid English learners. Generate JSON for response:"""
    dt_response = {}
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
            system_instruction=prompt,
            generation_config=generation_config,
        )
        test_response = model.generate_content(inputUser)
        data_response = test_response.text
        try:
            dt_response = json.loads(data_response)
        except:
            print("Invalid JSON response from API.")
    except requests.RequestException as e:
        print(f"Error in API request: {str(e)}")
    return dt_response


@login_required
def practice_create(request):
    nguoi_dung = request.user
    profile = nguoi_dung.profile

    if (
        not profile.is_premium
        and profile.created_questions_today >= profile.daily_question_limit
    ):
        messages.error(
            request,
            "Bạn đã hết lượt tạo câu hỏi hôm nay. Vui lòng nâng cấp tài khoản để sử dụng thêm.",
        )
        return redirect("practice_index")

    try:
        inputText = request.POST.get("inputText").strip()
        numQuestions = request.POST.get("numQuestions")
        typeQuestions = request.POST.get("typeQuestions")
    except (ValueError, json.JSONDecodeError):
        messages.warning(request, "Đã xảy ra lỗi, vui lòng thử lại.")
        return redirect("practice_index")
    dt_response = prompt_to_test(typeQuestions, numQuestions, inputText)

    if not dt_response:
        messages.warning(
            request, "Không thể tạo câu hỏi từ nội dung đã cung cấp. Vui lòng thử lại."
        )
        return redirect("practice_index")

    deThi = save_question(dt_response, user=nguoi_dung)

    if profile.created_questions_today < profile.daily_question_limit:
        profile.created_questions_today += 1
        profile.save()

    return redirect("practice_start", deThi_id=deThi.deThi_id)


@login_required
def practice_start(request, deThi_id):
    deThi = DeThi.objects.get(deThi_id=deThi_id)
    cauHois = CauHoi.objects.all().filter(deThi=deThi)
    response = render(
        request, "thq_exams/practice_page.html", {"deThi": deThi, "cauHois": cauHois}
    )
    response.set_cookie("deThi_id", deThi.deThi_id)
    return response


@login_required
def toggle_status(request, deThi_id):
    deThi = get_object_or_404(DeThi, deThi_id=deThi_id)
    deThi.trangThai = not deThi.trangThai
    deThi.save()
    return JsonResponse({"success": True, "new_status": deThi.trangThai})


@login_required
def submit_answers(request, deThi_id):
    if request.method == "POST":
        data = json.loads(request.body)
        cau_hoi_ids = data.get("cauHoi_ids", [])
        dap_an_chon = data.get("dapAnChon", [])
        nguoi_dung = request.user

        total_correct = 0
        results = []

        for cauHoi_id, dapAnChon in zip(cau_hoi_ids, dap_an_chon):
            try:
                cauHoi = CauHoi.objects.get(cauHoi_id=cauHoi_id)
                is_correct = cauHoi.dapAnDung == dapAnChon
                if is_correct:
                    total_correct += 1

                results.append(
                    {
                        "cauHoi_id": cauHoi_id,
                        "is_correct": is_correct,
                        "correct_answer": cauHoi.dapAnDung,
                        "explanation": cauHoi.giaiThich or "No explanation available.",
                    }
                )
            except CauHoi.DoesNotExist:
                continue

        total_questions = len(cau_hoi_ids)
        deThi = DeThi.objects.get(deThi_id=deThi_id)
        diem_so = (
            int((total_correct / total_questions) * 100) if total_questions > 0 else 0
        )
        ket_qua = KetQua.objects.create(
            deThi=deThi,
            nguoiDung=nguoi_dung,
            diemSo=diem_so,
        )

        return JsonResponse(
            {
                "total_questions": total_questions,
                "total_correct": total_correct,
                "results": results,
            }
        )
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def submit_test(request, deThi_id):
    if request.method == "POST":
        deThi = DeThi.objects.get(deThi_id=deThi_id)
        data = json.loads(request.body)
        cau_hoi_ids = data.get("cauHoi_ids", [])
        dap_an_chon = data.get("dapAnChon", [])
        nguoi_dung = request.user

        total_correct = 0
        results = []

        ket_qua = KetQua.objects.create(
            deThi=deThi,
            nguoiDung=nguoi_dung,
            diemSo=0,
            loai=True,
        )

        for cauHoi_id, dapAnChon in zip(cau_hoi_ids, dap_an_chon):
            try:
                cauHoi = CauHoi.objects.get(cauHoi_id=cauHoi_id)
                is_correct = cauHoi.dapAnDung == dapAnChon
                if is_correct:
                    total_correct += 1
            
                LuaChon.objects.create(
                    cauHoi=cauHoi, nguoiDung=nguoi_dung, dapAnChon=dapAnChon, ketQua=ket_qua
                )

                results.append(
                    {
                        "cauHoi_id": cauHoi_id,
                        "is_correct": is_correct,
                        "correct_answer": cauHoi.dapAnDung,
                        "explanation": cauHoi.giaiThich or "No explanation available.",
                    }
                )
            except CauHoi.DoesNotExist:
                continue

        total_questions = len(cau_hoi_ids)
        diem_so = (
            int((total_correct / total_questions) * 100) if total_questions > 0 else 0
        )
        ket_qua.diemSo = diem_so
        ket_qua.save()

        return JsonResponse(
            {
                "total_questions": total_questions,
                "total_correct": total_correct,
                "results": results,
            }
        )
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def test_start(request, deThi_id):
    deThi = DeThi.objects.get(deThi_id=deThi_id)
    cauHois = CauHoi.objects.all().filter(deThi=deThi)
    return render(
        request, "thq_exams/test_page.html", {"deThi": deThi, "cauHois": cauHois}
    )


@login_required
def vocab_search(request):
    if request.method != "POST":
        return JsonResponse({"response": "Invalid request"}, status=400)

    data = json.loads(request.body)
    word = data.get("word", "")

    prompt = """
    {
      "input": ... (The input word),
      "IPA": ... (The International Phonetic Alphabet notation of the word),
      "word_form": (The grammatical category of the word, e.g., noun, verb, adjective),
      "synonyms": ... (Two simple synonyms of the word),
      "vietnamese_meaning": ... (The meaning of the word in Vietnamese),
      "examples": [
        ... (First example sentence using the phrase),
        ... (Second example sentence using the phrase)
      ],
      "short_paragraph": ... (A short paragraph of 3 sentences using the phrase),
      "short_paragraph_Vietnamese": ... (A Vietnamese translation of the short paragraph of 3 sentences),
    }
    """
    inputUser = f"""Generate a detailed dictionary entry for the word '{ word }' based on the following format. Use the provided sentence context to tailor the examples and definitions:"""
    try:
        genai.configure(api_key=API_KEY)

        generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 20,
            "max_output_tokens": 2000,
            "response_mime_type": "application/json",
        }

        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=prompt,
            generation_config=generation_config,
        )
        vocab_response = model.generate_content(inputUser)
        data_response = vocab_response.text
        try:
            dt_vocab = json.loads(data_response)
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON response from API."}, status=500
            )
    except requests.RequestException as e:
        return JsonResponse({"response": f"Error in API request: {str(e)}"}, status=500)

    return JsonResponse(dt_vocab, status=200)

@login_required
def history_view(request):
    user = request.user
    ketQuas = (
        KetQua.objects.filter(
            nguoiDung=user, loai=True
        )  # Bộ lọc loai=True và người dùng hiện tại
        .annotate(
            tenDeThi=F("deThi__tenDeThi"), tenNguoiTao=F("deThi__nguoiTao__username")
        )
        .values("ketQua_id", "tenDeThi", "tenNguoiTao", "diemSo", "loai", "ngayTao")
    )
    return render(request, "thq_exams/test_history.html", {"ketQuas": ketQuas})

@login_required
def test_result(request, ketQua_id):
    ketQua = get_object_or_404(KetQua, ketQua_id=ketQua_id)

    lua_chons = LuaChon.objects.filter(ketQua=ketQua)

    results = []

    for lua_chon in lua_chons:
        cauHoi = lua_chon.cauHoi
        is_correct = cauHoi.dapAnDung == lua_chon.dapAnChon
        results.append({
            'cauHoi': cauHoi,
            'is_correct': is_correct,
            'dapAnChon': lua_chon.dapAnChon,
            'correct_answer': cauHoi.dapAnDung,
            'explanation': cauHoi.giaiThich or "No explanation available.",
        })

    return render(request, "thq_exams/test_result.html", {
        "ketQua": ketQua,
        "results": results,
    })
