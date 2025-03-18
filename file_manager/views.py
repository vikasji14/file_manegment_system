from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse, Http404
import os
from urllib.parse import unquote
from datetime import datetime,timedelta

# Set your root path
# ROOT_PATH = "D:/Desktop/ativiti/data"
ROOT_PATH = "C:/Users/vikas/Downloads/old_data"
UPLOAD_DIR = os.path.join(ROOT_PATH, 'uploads')

def index(request, path=""):
    # Combine ROOT_PATH with the provided path
    current_path = os.path.join(ROOT_PATH, path).replace("\\", "/")

    # Check if path exists
    if not os.path.exists(current_path):
        return HttpResponse("Path does not exist", status=404)

    if request.method == 'POST':
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            return redirect('folder_view', path=path) if path else redirect('/')

        if 'folder_name' in request.POST:
            folder_name = request.POST['folder_name']
            new_folder_path = os.path.join(current_path, folder_name)
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
            return redirect('folder_view', path=path) if path else redirect('/')

    if request.method == 'GET':
        if 'delete' in request.GET:
            delete_path = os.path.join(current_path, request.GET['delete'])
            if os.path.exists(delete_path):
                if os.path.isdir(delete_path):
                    os.rmdir(delete_path)
                else:
                    os.remove(delete_path)
            return redirect('folder_view', path=path or ROOT_PATH)

        if 'download' in request.GET:
            download_path = os.path.join(current_path, unquote(request.GET['download']))
            if os.path.exists(download_path) and os.path.isfile(download_path):
                response = FileResponse(open(download_path, 'rb'), as_attachment=True)
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(download_path)}"'
                return response
            else:
                raise Http404("File Not Found")

        if 'view' in request.GET:
            view_path = os.path.join(current_path, request.GET['view'])
            if os.path.exists(view_path) and os.path.isfile(view_path):
                return FileResponse(open(view_path, 'rb'))
            else:
                raise Http404("File not found")

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    items = []
    for item in os.listdir(current_path):
        item_path = os.path.join(current_path, item).replace("\\", "/")
        is_folder = os.path.isdir(item_path)

        last_modified = datetime.fromtimestamp(os.path.getmtime(item_path))
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, '%d/%m/%Y')
            end_dt = datetime.strptime(end_date, '%d/%m/%Y')
            end_dt += timedelta(days=1) - timedelta(seconds=1)

# Compare only the date parts
            if not (start_dt <= last_modified <= end_dt):
                continue

        file_size = "-"
        if not is_folder:
            size_bytes = os.path.getsize(item_path)
            if size_bytes < 1024:
                file_size = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                file_size = f"{size_bytes / 1024:.2f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                file_size = f"{size_bytes / (1024 * 1024):.2f} MB"
            else:
                file_size = f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

        items.append({
            'name': item,
            'is_folder': is_folder,
            'path': f"{path}/{item}".lstrip("/"),
            'size': file_size,
            'last_modified': last_modified.strftime('%d/%m/%Y')
        })

    breadcrumbs = []
    parts = path.split("/")
    for i, part in enumerate(parts):
        if part:
            breadcrumbs.append({
                'name': part,
                'path': "/".join(parts[:i + 1])
            })
    return render(request, 'file_manager.html', {
        'items': items,
        'breadcrumbs': breadcrumbs,
        'current_path': path,
        'start_date': start_date,
        'end_date': end_date
    })
