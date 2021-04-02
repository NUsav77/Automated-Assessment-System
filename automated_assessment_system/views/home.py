from django.shortcuts import render
from django.views import View


class HomeView(View):
    template_name = "home.html"

    def get(self, *args, **kwargs):
        return render(
            self.request,
            self.template_name,
            context={
                "application_name": "Welcome to the Automated Assessment System",
                "message": "hello",
            },
        )
