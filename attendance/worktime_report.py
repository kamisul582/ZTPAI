from django.http import JsonResponse
from django.views.generic import View
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
from django.shortcuts import render
import calendar
from .models import Worktime
from .views import get_employed_user_ids_json,get_worker_from_user,get_employed_user_ids
from django.http import HttpResponse
from openpyxl import Workbook
import tempfile
import xlsxwriter
import io
from datetime import timedelta

class WorktimeExportView(View):
    def get(self, request, *args, **kwargs):
        if 'year' not in request.GET and 'month' not in request.GET:
            current_year = timezone.now().year
            years = list(range(current_year - 5, current_year + 1))
            months = {i: calendar.month_name[i] for i in range(1, 13)}
            workers = get_employed_user_ids(request)
            print(workers)
            return render(request, 'attendance/worktime_export.html', {'years': years, 'months': months,'workers':workers})
        if 'year' in request.GET and 'month' in request.GET:
            month = int(request.GET.get('month'))
            year = int(request.GET.get('year'))
            worker = request.GET.get('worker')
            worker_id=int(worker[0]) if worker else ""
            print("month,year,worker_id",month,year,worker_id)
            start_date = datetime(year, month, 1)
            end_date = datetime(year, month % 12 + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
            workers = get_employed_user_ids(request)
            print(workers)
            worktimes = Worktime.objects.filter(worker_id__in=workers,date__gte=start_date, date__lt=end_date)
            if worker_id:
                print("worker_id",worker_id,type(worker_id))
                worktimes = worktimes.filter(worker_id=worker_id)
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet()
            headers = ["Firstname","Lastname", "Date", "Punch In", "Punch Out", "Total Time","Sum"]
            for col, header in enumerate(headers):
                worksheet.write(0, col, header)
            row = 1
            
            if worktimes:
                temp_worker = worktimes[0].worker
            worker_data=f"_{temp_worker.firstname}_{temp_worker.lastname}" if worker and worktimes else ""
            temp_worktime = timedelta(seconds=0)
            for worktime in worktimes:
                worksheet.write(row, 0, worktime.worker.firstname)
                worksheet.write(row, 1, worktime.worker.lastname)
                worksheet.write(row, 2, worktime.date.strftime('%Y-%m-%d'))
                worksheet.write(row, 3, worktime.punch_in.strftime('%Y-%m-%d %H:%M:%S') if worktime.punch_in else '')
                worksheet.write(row, 4, worktime.punch_out.strftime('%Y-%m-%d %H:%M:%S') if worktime.punch_out else '')
                worksheet.write(row, 5, str(worktime.total_time) if worktime.total_time else '')
                temp_worktime+=worktime.total_time
                print(worktime.total_time,type(worktime.total_time))
                if temp_worker!=worktime.worker:
                    print("in if",temp_worker,"\n",worktime.worker)
                    worksheet.write(row-1, 6, str(temp_worktime))
                    temp_worktime = timedelta(seconds=0)
                    temp_worker=worktime.worker
                
                row += 1
            worksheet.write(row-1, 6, str(temp_worktime))
            workbook.close()
            
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{month}_{year}{worker_data}_worktime_export.xlsx"'
            response.write(output.getvalue())
            return response
            

def worktime_export(request):
    worktime_export_view = WorktimeExportView()
    response = worktime_export_view.get(request)
    return response