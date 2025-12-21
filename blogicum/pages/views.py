from django.shortcuts import render
from django.views.generic import TemplateView


def handler403(request, exception):
    template = 'pages/403csrf.html'
    return render(request, template, status=403)


def handler404(request, exception):
    template = 'pages/404.html'
    return render(request, template, status=404)


def handler500(request):
    template = 'pages/500.html'
    return render(request, template, status=500)


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'
