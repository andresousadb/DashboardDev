from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm, UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from .dados import get_data_postgres
import json


def auth_signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            print('Account created successfully!')
            return redirect('/accounts/auth-signin/')
        else:
            print("Registration failed!")
    else:
        form = RegistrationForm()
    context = {'form': form}
    return render(request, 'accounts/auth-signup.html', context)


class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/forgot-password.html'
    form_class = UserPasswordResetForm


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/recover-password.html'
    form_class = UserSetPasswordForm


class UserPasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = UserPasswordChangeForm


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/recover-password.html'
    form_class = UserSetPasswordForm


def user_logout_view(request):
    logout(request)
    return redirect('/accounts/auth-signin/')


class AuthSignin(LoginView):
    template_name = 'accounts/auth-signin.html'
    form_class = LoginForm
    success_url = '/'  # Defina a URL padrão para redirecionamento após o login


def dashboard(request):
    dados_json_str = get_data_postgres()
    dados_json = json.loads(dados_json_str)

    total_id = 0
    total_id_aberto = 0
    total_dentro_prazo = 0
    total_fora_prazo = 0

    aguardando = [item for item in dados_json if item['status'] == 1 and item['responsavel'] is None]
    em_atendimento = [item for item in dados_json if item['status'] == 1 and item['responsavel'] is not None]
    atendido = sorted([item for item in dados_json if item['status'] == 6 ],key=lambda x: x['dt_encerrado'],reverse=True)[:30]

    for total in dados_json:
        if 'id' in total and total['status'] == 6:
            total_id += 1

    for total_aberto in dados_json:
        if 'id' in total_aberto and total_aberto['status'] == 1:
            total_id_aberto += 1

    for prazo in dados_json:
        if 'id' in prazo and prazo['prazo'] == 1 and prazo['status'] == 6:
            total_dentro_prazo += 1

    for fora in dados_json:
        if 'id' in fora and fora['prazo'] == 0 and fora['status'] == 6:
            total_fora_prazo += 1


    context = {
        'parent': 'pages',
        'segment': 'dashboard',
        'aguardando': aguardando,
        'em_atendimento': em_atendimento,
        'atendido': atendido,
        'total_id':total_id,
        'total_id_aberto': total_id_aberto,
        'total_fora_prazo':total_fora_prazo,
        'total_dentro_prazo':total_dentro_prazo,

    }

    return render(request, 'pages/dashboard.html', context)
