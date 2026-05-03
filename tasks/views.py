from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from . import models
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User


class TaskListView(ListView):
    model = models.Task
    context_object_name = "tasks"
    template_name = "tasks/task_list.html"


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = models.Task
    context_object_name = "task"
    template_name = "tasks/task_detail.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        content = request.POST.get('content')
        if content:
            models.Comment.objects.create(
                task=self.object,
                author=request.user,
                content=content
            )
        return redirect('tasks:task_detail', pk=self.object.pk)


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = models.Task
    fields = ['title', 'description', 'priority', 'status']
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("tasks:task_list")

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Task
    fields = ['title', 'description', 'priority', 'status']
    template_name = "tasks/task_form.html"

    def get_success_url(self):
        return reverse_lazy("tasks:task_detail", kwargs={"pk": self.object.pk})


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Task
    template_name = "tasks/task_delete_confirmation.html"  # Твое название файла
    success_url = reverse_lazy("tasks:task_list")


# Заглушки для URL-ов, чтобы сервер не падал
class RegisterView(View):
    template_name = "tasks/register.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        # Получаем данные из нашей новой формы
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        p_conf = request.POST.get('password_confirm')
        invite = request.POST.get('invite_code')

        # 1. Проверяем инвайт
        if invite != "skeet":
            return render(request, self.template_name, {'error': 'Invalid invite code'})

        # 2. Проверяем совпадение паролей
        if p_word != p_conf:
            return render(request, self.template_name, {'error': 'Passwords do not match'})

        # 3. Проверяем, не занят ли ник
        if User.objects.filter(username=u_name).exists():
            return render(request, self.template_name, {'error': 'Username already taken'})

        # 4. Создаем юзера
        user = User.objects.create_user(username=u_name, password=p_word)
        login(request, user)
        return redirect('tasks:task_list')

class CustomLoginView(LoginView):
    template_name = "tasks/login.html"
    next_page = reverse_lazy("tasks:task_list")


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("tasks:task_list")


class CommentUpdateView(UpdateView):
    model = models.Comment
    fields = ['content']
    template_name = "tasks/task_form.html"


class CommentDeleteView(DeleteView):
    model = models.Comment
    template_name = "tasks/task_delete_confirmation.html"


class CommentLikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(models.Comment, pk=pk)
        # Проверяем, ставил ли этот юзер уже лайк
        like = models.Like.objects.filter(comment=comment, user=request.user)

        if like.exists():
            like.delete()  # Если лайк есть — убираем
        else:
            models.Like.objects.create(comment=comment, user=request.user)  # Если нет — создаем

        return redirect('tasks:task_detail', pk=comment.task.pk)


class TaskCompleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        return redirect('tasks:task_list')
