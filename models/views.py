from django.views.generic import DetailView, ListView, TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin  # Mixin import qilindi
from .models import Candidate, Vacancy
from .utils import QUESTIONS


class CandidateDetailView(LoginRequiredMixin, DetailView):
    model = Candidate
    template_name = 'candidate_detail.html'
    context_object_name = 'candidate'

    # Agar foydalanuvchi login qilmagan bo'lsa, qayerga yo'naltirish (ixtiyoriy, settingsda berilsa shart emas)
    # login_url = '/admin/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        candidate = self.get_object()
        qa_list = []
        for q in QUESTIONS:
            qa_list.append({
                'question': q['text'],
                'answer': candidate.answers.get(q['key'], '-'),
                'type': q['type']
            })
        context['qa_list'] = qa_list
        context['status_choices'] = Candidate.STATUS_CHOICES
        return context

    def post(self, request, *args, **kwargs):
        candidate = self.get_object()
        new_status = request.POST.get('status')
        if new_status in dict(Candidate.STATUS_CHOICES):
            candidate.status = new_status
            candidate.save()
            messages.success(request, f"Nomzod statusi '{candidate.get_status_display()}' holatiga o'zgartirildi.")
        return redirect('candidate_detail', pk=candidate.pk)


class CandidateListView(LoginRequiredMixin, ListView):
    model = Candidate
    template_name = 'candidate_list.html'
    context_object_name = 'candidates'
    paginate_by = 15

    def get_queryset(self):
        queryset = Candidate.objects.select_related('vacancy').all()

        vacancy_id = self.request.GET.get('vacancy')
        if vacancy_id:
            queryset = queryset.filter(vacancy_id=vacancy_id)

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(full_name__icontains=search) | queryset.filter(phone__icontains=search)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vacancies'] = Vacancy.objects.all()
        context['status_choices'] = Candidate.STATUS_CHOICES
        context['current_vacancy'] = self.request.GET.get('vacancy')
        context['current_status'] = self.request.GET.get('status')
        context['current_search'] = self.request.GET.get('search')
        return context



class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'