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

class WorktimeExportView(View):
    def get(self, request, *args, **kwargs):
        # Get parameters
        month = int(request.GET.get('month', timezone.now().month))
        year = int(request.GET.get('year', timezone.now().year))
        worker_id = request.GET.get('worker_id')
        print("month,year,worker_id",month,year,worker_id)
        # Calculate start and end date for the given month
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month % 12 + 1, 1) if month < 12 else datetime(year + 1, 1, 1)

        # Query based on parameters
        worktimes = Worktime.objects.filter(date__gte=start_date, date__lt=end_date)
        if worker_id:
            worktimes = worktimes.filter(worker_id=worker_id)


        workbook = xlsxwriter.Workbook(filename='worktime_export.xlsx')
        worksheet = workbook.add_worksheet()

        # Write headers
        headers = ["Worker", "Date", "Punch In", "Punch Out", "Total Time"]
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)

        # Write data rows
        row = 1
        for worktime in worktimes:
            worksheet.write(row, 0, worktime.worker.firstname)
            worksheet.write(row, 1, worktime.date.strftime('%Y-%m-%d'))
            worksheet.write(row, 2, worktime.punch_in.strftime('%Y-%m-%d %H:%M:%S') if worktime.punch_in else '')
            worksheet.write(row, 3, worktime.punch_out.strftime('%Y-%m-%d %H:%M:%S') if worktime.punch_out else '')
            worksheet.write(row, 4, str(worktime.total_time) if worktime.total_time else '')
            row += 1

        # Close the workbook
        workbook.close()

        # Read the contents of the workbook
        with open('worktime_export.xlsx', 'rb') as file:
            content = file.read()
        #wb = Workbook()
        #ws = wb.active
        #ws.append(["Worker", "Date", "Punch In", "Punch Out", "Total Time"])
        #for worktime in worktimes:
        #    # Convert datetime values to naive datetimes
        #    punch_in = worktime.punch_in.replace(tzinfo=None) if worktime.punch_in else None
        #    punch_out = worktime.punch_out.replace(tzinfo=None) if worktime.punch_out else None
        #    
        #    ws.append([worktime.worker.firstname, worktime.date, punch_in, punch_out, worktime.total_time])
        #with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        #    wb.save(tmpfile.name)
        #    # Read the content of the file after saving
        #    tmpfile.seek(0)
        #    content = tmpfile.read()
        

        # Serialize the data
        data = []
        for worktime in worktimes:
            data.append({
                'worker': worktime.worker.firstname,
                'date': worktime.date,
                'punch_in': worktime.punch_in,
                'punch_out': worktime.punch_out,
                'total_time': str(worktime.total_time) if worktime.total_time else None,
            })
        print(data)
        #return JsonResponse(data, safe=False)
        response = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="worktime_export.xlsx"'

        return response


def worktime_export(request):
    current_year = timezone.now().year
    years = list(range(current_year - 5, current_year + 1))  # Range of years from 5 years ago to the current year
    months = {i: calendar.month_name[i] for i in range(1, 13)}  # Dictionary of month numbers to month names

    worktime_export_view = WorktimeExportView()
    worktime_entries = worktime_export_view.get(request)
    #print(worktime_entries)
    workers = get_employed_user_ids(request)
    #print(worker_user)
    #workers=[]
    #for worker_user in worker_user:
    #    workers.append(get_worker_from_user(worker_user.id))
    print(workers)
    print()
    return worktime_entries
    #return render(request, 'attendance/worktime_export.html', {'workers':workers,'years': years, 'months': months, 'worktime_entries': worktime_entries})
