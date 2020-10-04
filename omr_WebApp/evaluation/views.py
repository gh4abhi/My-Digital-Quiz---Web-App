from django.shortcuts import render
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from evaluation.omr import VideoStream


def home(request):
    return render(request,"evaluation/home.html")

def check(request):
    return render(request,"evaluation/check.html")


def about(request):
	return render(request,'evaluation/aboutus.html',{'title':"About Us"})  

def StreamView(object):
    while True:
        frame = object.get_frame()
        yield(b'--frame\r\n'
            b'content-type: image\r\n\r\n' + frame + b'\r\n\r\n')
def contact(request):
    return render(request,'evaluation/contactus.html',{'title':"Contact Us"})


def VideoFeed(request):
    return StreamingHttpResponse(StreamView(VideoStream()), content_type = 'multipart/x-mixed-replace; boundary=frame')    
