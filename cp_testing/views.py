from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
import subprocess
import os
import requests
from bs4 import BeautifulSoup
import time


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
    if pro1[1].decode() != "":
        return data, pro1[1].decode()
    for p, x, y, z, w, t in data:
        lst = [p, x]
        start = time.time()
        proc = subprocess.Popen(["a.exe"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        proc = proc.communicate(input=x.encode())[0]
        end = time.time()
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
        lst.append(str(round((end-start)*100, 2))+" ms")
        pdata.append(lst)
    os.remove("a.exe")
    return pdata, ""


def get_data(site):
    res = requests.get(site)
    soup = BeautifulSoup(res.content, 'html.parser')
    status = res.status_code
    if int(status) != 200:
        txt = "Status Code Received: " + str(status) + "\n"
        txt += "Invalid URL... Please Enter a Valid URL"
        return [], txt
    try:
        code = soup.select('div.sample-test')[0]
        inputs = []
        inp = code.select('div.input')
        for x in inp:
            txt = x.select('pre')[0].prettify()
            txt = txt.replace("<pre>", "")
            txt = txt.replace("</pre>", "")
            txt = txt.replace("<br/>", " ")
            inputs.append("\n".join(txt.split(" ")))
        out = code.select('div.output')
        outputs = []
        for x in out:
            txt = x.select('pre')[0].prettify()
            txt = txt.replace("<pre>", "")
            txt = txt.replace("</pre>", "")
            txt = txt.replace("<br/>", "-$-$")
            outputs.append("\n".join(txt.split("-$-$")))
        data = []
        for x in range(len(inputs)):
            data.append((x+1, inputs[x], "", outputs[x], "", ""))
        return data, ""
    except Exception as e:
        txt = "Invalid URL... Please Enter a Valid URL"
        return [], txt


def delete_files(dirs):
    if len(dirs) > 5:
        dirs.sort()
        dirs = dirs[:-5]
        for x in dirs:
            name = os.path.join("data", str(x)+".cpp")
            os.remove(name)


def index(request):
    data = [(1, "", "", "", "", "")]
    context = {
        "data": data,
        "num": len(data),
        "file_url": "",
        "err": "",
        "errors": (),
        "num_errors": 0,
        "code_site": "",
    }
    if request.method == 'POST':
        file = request.FILES.get('cpp_file')
        if request.POST.get("code_url") is not None:
            code_site = request.POST.get("code_url")
        else:
            code_site = ""
        dirs = os.listdir("data/")
        pdirs = []
        for x in dirs:
            x = x.replace(".cpp", "")
            x = x.replace(".c", "")
            pdirs.append(int(x))
        delete_files(pdirs)
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
            lst.append("")
            ptr = "et" + str(i)
            if request.POST.get(ptr) is not None:
                lst.append(request.POST.get(ptr))
            else:
                lst.append("")
            lst.append("")
            lst.append("")
            data.append(lst)
            i += 1
        if request.POST.get("same_file") != "on":
            handle_uploaded_file(file, name)
        else:
            if len(pdirs) != 0:
                name = str(max(pdirs))+".cpp"
            else:
                if len(data) == 0:
                    data = [(1, "", "", "", "", "")]
                context = {
                    "data": data,
                    "num": len(data),
                    "file_url": "",
                    "err": "",
                    "errors": (),
                    "num_errors": 0,
                    "code_site": code_site,
                }
                return render(request, "homepage.html", context)
        if code_site != "":
            cdata, msg = get_data(code_site)
            n = len(data)
            for x, y, z, w, p, t in cdata:
                data.append((n+1, y, z, w, p, t))
                n += 1
        else:
            msg = ""
        data, err = testing(data, name)
        if len(data) == 0:
            data = [(1, "", "", "", "", "")]
        context = {
            "data": data,
            "num": len(data),
            "file_url": "/files/"+name,
            "err": "present",
            "errors": zip(range(len(err.splitlines())), err.splitlines()),
            "num_errors": len(err.splitlines()),
            "code_site": code_site,
            "msg" : msg,
        }
        return render(request, "homepage.html", context)
    return render(request, "homepage.html", context)
