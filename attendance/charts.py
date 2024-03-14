from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
from .models import CustomUser, Worktime, Company, Worker

class LineChartJSONView(BaseLineChartView):
    extra_data = None  # Define a class variable to store extra data
    #user_id = None
    def get_labels(self):
        """Return labels for the x-axis based on your model data and extra data."""
        # Replace this with your actual logic to get date labels from your model
        user_id = self.request.GET.get('user_id')
        worker = Worker.objects.get(user_id=user_id)
        labels_from_model = [str(entry.date) for entry in Worktime.objects.filter(worker_id=worker)]

        if self.extra_data:
            # Combine model data labels with extra data labels
            labels_from_model += self.extra_data.get('labels', [])

        return labels_from_model

    def get_providers(self):
        """Return names of datasets."""
        return ["Employee worktime"]
    
    def get_colors(self):
        """
        Return colors for the datasets.

        Override this method to provide custom colors.
        """
        colors = [(255, 87, 51)]  # Example color as RGB tuple
        return iter(colors)

    
    def get_data(self):
        """Return datasets to plot based on your model data and extra data."""
        user_id = self.request.GET.get('user_id')
        worker = Worker.objects.get(user_id=user_id)
        total_time = [round(entry.total_time.total_seconds()/60,1) for entry in Worktime.objects.filter(worker_id=worker)]
        name_data = [entry.name for entry in Company.objects.all()]

        
        
        return [total_time]

template = TemplateView.as_view(template_name='attendance/charts.html')
line_chart_json = LineChartJSONView.as_view()