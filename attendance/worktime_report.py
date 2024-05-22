from django.http import JsonResponse, HttpResponse
from django.views.generic import View
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, timedelta
from openpyxl import Workbook
import io
import calendar
import xlsxwriter
from .models import Worktime
from .views import get_employed_worker_ids

class WorktimeExportView(View):
    def get(self, request, *args, **kwargs):
        if not request.GET.get('year') or not request.GET.get('month'):
            return self.render_initial_page(request)
        
        return self.generate_worktime_report(request)
    
    def render_initial_page(self, request):
        current_year = timezone.now().year
        years = list(range(current_year - 5, current_year + 1))
        months = {i: calendar.month_name[i] for i in range(1, 13)}
        workers = get_employed_worker_ids(request)
        return render(request, 'attendance/worktime_export.html', {'years': years, 'months': months, 'workers': workers})

    def generate_worktime_report(self, request):
        month = int(request.GET.get('month'))
        year = int(request.GET.get('year'))
        worker = request.GET.get('worker')
        worker_id = int(worker.split(".")[0]) if worker else None
        start_date, end_date = self.get_date_range(year, month)
        workers = get_employed_worker_ids(request)
        worktimes = self.get_filtered_worktimes(workers, start_date, end_date, worker_id)
        output, worker_data = self.create_workbook(worktimes, worker)
        response = self.build_response(output, month, year, worker_data)
        return response

    def get_date_range(self, year, month):
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month % 12 + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
        return start_date, end_date

    def get_filtered_worktimes(self, workers, start_date, end_date, worker_id):
        worktimes = Worktime.objects.filter(worker_id__in=workers, date__gte=start_date, date__lt=end_date)
        if worker_id:
            worktimes = worktimes.filter(worker_id=worker_id)
        return worktimes

    def build_response(self, output, month, year, worker_data):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{month}_{year}{worker_data}_worktime_export.xlsx"'
        response.write(output.getvalue())
        return response
    
    def create_workbook(self, worktimes, worker):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        headers = ["Firstname", "Lastname", "Date", "Punch In", "Punch Out", "Total Time", "Sum"]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)

        row = 1
        temp_worktime = timedelta(seconds=0)
        temp_worker = worktimes[0].worker if worktimes else None
        worker_data = f"_{temp_worker.firstname}_{temp_worker.lastname}" if worker and worktimes else ""

        for worktime in worktimes:
            worksheet.write(row, 0, worktime.worker.firstname)
            worksheet.write(row, 1, worktime.worker.lastname)
            worksheet.write(row, 2, worktime.date.strftime('%Y-%m-%d'))
            worksheet.write(row, 3, worktime.punch_in.strftime('%Y-%m-%d %H:%M:%S') if worktime.punch_in else '')
            worksheet.write(row, 4, worktime.punch_out.strftime('%Y-%m-%d %H:%M:%S') if worktime.punch_out else '')
            worksheet.write(row, 5, str(worktime.total_time) if worktime.total_time else '')
            temp_worktime += worktime.total_time
            
            if temp_worker != worktime.worker:
                worksheet.write(row - 1, 6, str(temp_worktime))
                temp_worktime = timedelta(seconds=0)
                temp_worker = worktime.worker

            row += 1

        worksheet.write(row - 1, 6, str(temp_worktime))
        workbook.close()
        return output, worker_data




def worktime_export(request):
    view = WorktimeExportView()
    return view.get(request)
