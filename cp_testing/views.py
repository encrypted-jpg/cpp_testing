from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
import subprocess
import os


def handle_uploaded_file(f, name):
    with open("data/" + name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def verify(out, eout):
    if len(out) != len(eout):
        return False
    for x in range(len(out)):
        if out[x].strip() != eout[x].strip():
            return False
    return True


def testing(data, name):
    pdata = []
    pro1 = subprocess.Popen(["g++", "data/" + name], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    pro1 = pro1.communicate()
    if pro1[1].decode() is not "":
        return data, pro1[1].decode()
    for p, x, y, z, w in data:
        lst = [p, x]
        proc = subprocess.Popen(["a.exe"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        proc = proc.communicate(input=x.encode())[0]
        out = proc.decode()
        lst.append(out)
        lst.append(z)
        pst = []
        kst = []
        for x in out.splitlines():
            if x.strip() != "":
                pst.append(x.strip())
        for x in z.splitlines():
            if x.strip() != "":
                kst.append(x.strip())
        if verify(pst, kst):
            lst.append("CORRECT")
        else:
            lst.append("INCORRECT")
        pdata.append(lst)
    os.remove("a.exe")
    return pdata, ""


def index(request):
    data = [(1, "", "", "", "")]
    context = {
        "data": data,
        "num": len(data),
        "file_url": "",
        "err": "",
        "errors": (),
        "num_errors": 0,
    }
    if request.method == 'POST':
        file = request.FILES.get('cpp_file')
        dirs = os.listdir("data/")
        pdirs = []
        for x in dirs:
            x = x.replace(".cpp", "")
            x = x.replace(".c", "")
            pdirs.append(int(x))
        if len(pdirs) == 0:
            name = "1.cpp"
        else:
            name = str(max(pdirs)+1)+".cpp"
        if file is None and request.POST.get("same_file") != "on":
            return render(request, "homepage.html", context)
        i = 1
        data = []
        while True:
            lst = []
            ptr = "tc" + str(i)
            if request.POST.get(ptr) == "":
                i += 1
                continue
            if request.POST.get(ptr) is not None:
                lst.append(i)
                lst.append(request.POST.get(ptr))
            else:
                break
            ptr = "ot" + str(i)
            if request.POST.get(ptr) is not None:
                lst.append(request.POST.get(ptr))
            else:
                lst.append("")
            ptr = "et" + str(i)
            if request.POST.get(ptr) is not None:
                lst.append(request.POST.get(ptr))
            else:
                lst.append("")
            ptr = "mt" + str(i)
            if request.POST.get(ptr) is not None:
                lst.append(request.POST.get(ptr))
            else:
                lst.append("")
            data.append(lst)
            i += 1
        if request.POST.get("same_file") != "on":
            handle_uploaded_file(file, name)
        else:
            if len(pdirs) != 0:
                name = str(max(pdirs))+".cpp"
            else:
                context = {
                    "data": data,
                    "num": len(data),
                    "file_url": "",
                    "err": "",
                    "errors": (),
                    "num_errors": 0,
                }
                return render(request, "homepage.html", context)
        data, err = testing(data, name)
        if len(data) == 0:
            data = [(1, "", "", "", "")]
        context = {
            "data": data,
            "num": len(data),
            "file_url": "/files/"+name,
            "err": "present",
            "errors": zip(range(len(err.splitlines())), err.splitlines()),
            "num_errors": len(err.splitlines()),
        }
        return render(request, "homepage.html", context)
    return render(request, "homepage.html", context)
