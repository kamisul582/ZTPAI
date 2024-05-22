from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
from .models import CustomUser, Worktime, Company, Worker
from django.core.exceptions import ObjectDoesNotExist
class LineChartJSONView(BaseLineChartView):
    extra_data = None
    def get_labels(self):
        user_id = self.request.GET.get('user_id')
        try:
            worker = Worker.objects.get(user_id=user_id)
        except ObjectDoesNotExist:
            return None
        labels_from_model = [str(entry.date) for entry in Worktime.objects.filter(worker_id=worker)]

        if self.extra_data:
            labels_from_model += self.extra_data.get('labels', [])

        return labels_from_model

    def get_data(self):
        user_id = self.request.GET.get('user_id')
        try:
            worker = Worker.objects.get(user_id=user_id)
        except ObjectDoesNotExist:
            return None
        total_time = [round(entry.total_time.total_seconds()/60,1) for entry in Worktime.objects.filter(worker_id=worker)]
        name_data = [entry.name for entry in Company.objects.all()]
        return [total_time]

    def get_providers(self):
        return ["Employee worktime"]
    
    def get_colors(self):
        colors = [(54, 162, 235)]
        return iter(colors)
template = TemplateView.as_view(template_name='attendance/charts.html')
line_chart_json = LineChartJSONView.as_view()