from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from allauth.account.utils import send_email_confirmation
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from thq_exams.models import KetQua
from django.db.models import Count, Avg, Case, When, Value
from datetime import datetime, timedelta
from django.db.models.functions import TruncDate
from django.contrib.auth.views import redirect_to_login
from django.contrib import messages
from .forms import *
import json


def profile_view(request, username=None):
    if username:
        nguoiDung = get_object_or_404(User, username=username)
        profile = nguoiDung.profile
    else:
        try:
            nguoiDung = request.user
            profile = nguoiDung.profile
        except:
            return redirect_to_login(request.get_full_path())
    start_date = datetime.now() - timedelta(days=30)

    line_results = (
        KetQua.objects.filter(nguoiDung=nguoiDung, ngayTao__gte=start_date)
        .annotate(day=TruncDate("ngayTao"))
        .values("day")
        .annotate(avg_score=Avg("diemSo"))
        .order_by("day")
    )
    line_data = {
        "labels": [result["day"].strftime("%Y-%m-%d") for result in line_results],
        "scores": [result["avg_score"] for result in line_results],
    }

    heatmap_results = (
        KetQua.objects.filter(nguoiDung=nguoiDung, ngayTao__gte=start_date)
        .annotate(day=TruncDate("ngayTao"))
        .values("day")
        .annotate(total=Count("ketQua_id"))
        .order_by("day")
    )
    heatmap_data = {
        result["day"].strftime("%Y-%m-%d"): result["total"]
        for result in heatmap_results
    }

    pie_data = (
        KetQua.objects.annotate(
            category=Case(
                When(diemSo__lte=40, then=Value("Thấp")),
                When(diemSo__lte=70, then=Value("Trung Bình")),
                When(diemSo__gt=70, then=Value("Cao")),
                default=Value("Không Xác Định"),
            )
        )
        .values("category")
        .annotate(count=Count("ketQua_id"))
    )

    pie_chart_data = {
        "labels": [entry["category"] for entry in pie_data],
        "counts": [entry["count"] for entry in pie_data],
    }
    return render(
        request,
        "thq_users/profile.html",
        {
            "profile": profile,
            "line_data": json.dumps(line_data),
            "heatmap_data": json.dumps(heatmap_data),
            "pie_chart_data": json.dumps(pie_chart_data),
        },
    )


@login_required
def profile_edit_view(request):
    form = ProfileForm(instance=request.user.profile)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect("profile")

    if request.path == reverse("profile-onboarding"):
        onboarding = True
    else:
        onboarding = False

    return render(
        request, "thq_users/profile_edit.html", {"form": form, "onboarding": onboarding}
    )


@login_required
def profile_settings_view(request):
    return render(request, "thq_users/profile_settings.html")


@login_required
def profile_emailchange(request):

    if request.htmx:
        form = EmailForm(instance=request.user)
        return render(request, "partials/email_form.html", {"form": form})

    if request.method == "POST":
        form = EmailForm(request.POST, instance=request.user)

        if form.is_valid():

            # Check if the email already exists
            email = form.cleaned_data["email"]
            if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                messages.warning(request, f"{email} is already in use.")
                return redirect("profile-settings")

            form.save()

            # Then Signal updates emailaddress and set verified to False

            # Then send confirmation email
            send_email_confirmation(request, request.user)

            return redirect("profile-settings")
        else:
            messages.warning(request, "Form not valid")
            return redirect("profile-settings")

    return redirect("home")


@login_required
def profile_emailverify(request):
    send_email_confirmation(request, request.user)
    return redirect("profile-settings")


@login_required
def profile_delete_view(request):
    user = request.user
    if request.method == "POST":
        logout(request)
        user.delete()
        messages.success(request, "Account deleted, what a pity")
        return redirect("home")

    return render(request, "thq_users/profile_delete.html")
