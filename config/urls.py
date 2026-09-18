from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from consultas.forms import LoginForm
urlpatterns = [
    path("admin/", admin.site.urls),
    path("entrar/", auth_views.LoginView.as_view(template_name="registration/login.html", authentication_form=LoginForm), name="login"),
    path("sair/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("consultas.urls")),
]
admin.site.site_header = "Saúde Viva • Administração"
admin.site.site_title = "Saúde Viva"
admin.site.index_title = "Gestão da clínica"
