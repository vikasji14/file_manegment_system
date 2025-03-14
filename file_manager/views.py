from django.shortcuts import render, redirect
from django.http import HttpResponse,FileResponse,Http404
import os
from urllib.parse import unquote

# Set your root path
ROOT_PATH = "C:/Users/Vikas/Desktop/project"

def index(request, path=""):
    # Combine ROOT_PATH with the provided path
    current_path = os.path.join(ROOT_PATH, path).replace("\\", "/")

    # Check if path exists
    if not os.path.exists(current_path):
        return HttpResponse("Path does not exist", status=404)

    # Handle file upload
    if request.method == 'POST':
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            file_path = os.path.join(current_path, uploaded_file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            return redirect('folder_view', path=path or ROOT_PATH)

        # Handle folder creation
        if 'folder_name' in request.POST:
            folder_name = request.POST['folder_name']
            new_folder_path = os.path.join(current_path, folder_name)
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
            return redirect('folder_view', path=path or ROOT_PATH)

    # Handle file/folder deletion
    if request.method == 'GET' and 'delete' in request.GET:
        delete_path = os.path.join(current_path, request.GET['delete'])
        if os.path.exists(delete_path):
            if os.path.isdir(delete_path):
                os.rmdir(delete_path)
            else:
                os.remove(delete_path)
        return redirect('folder_view', path=path or ROOT_PATH)
    
    # Download file
    if request.method == 'GET' and 'download' in request.GET:
        download_path = os.path.join(current_path, unquote(request.GET['download']))
        if os.path.exists(download_path) and os.path.isfile(download_path):
        # Open the file and return as attachment
            response = FileResponse(open(download_path, 'rb'), as_attachment=True)
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(download_path)}"'
            return response
        else:
            raise Http404("File Not Found")
            
    # Handle file view
    if request.method == 'GET' and 'view' in request.GET:
        view_path = os.path.join(current_path, request.GET['view'])
        if os.path.exists(view_path) and os.path.isfile(view_path):
            return FileResponse(open(view_path, 'rb'))
        else:
            raise Http404("File not found")
    
    # Get files and folders inside the current path
    items = []
    for item in os.listdir(current_path):
        item_path = os.path.join(current_path, item).replace("\\", "/")
        items.append({
            'name': item,
            'is_folder': os.path.isdir(item_path),
            'path': f"{path}/{item}".lstrip("/")
        })

    # Breadcrumbs
    breadcrumbs = []
    parts = path.split("/")
    for i, part in enumerate(parts):
        if part:
            breadcrumbs.append({
                'name': part,
                'path': "/".join(parts[:i + 1])
            })

    # Pass to template
    return render(request, 'index.html', {
        'items': items,
        'breadcrumbs': breadcrumbs,
        'current_path': path
    })

