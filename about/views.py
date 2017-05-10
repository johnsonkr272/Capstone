from django.shortcuts import render, redirect
from django.core.files import File
from django.http import HttpResponse
from about.models import Document
from about.forms import DocumentForm
from collections import defaultdict
from about.creds import stt
import json
import subprocess, os, sox, pdb
from django.core.files.storage import FileSystemStorage


def about(request):
    return render(request, 'about/includes/homepage.html')

def model_form_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():    
            #pdb.set_trace() #Python debugger
            form.save() 
            filename = request.FILES['document'].name
            filename2 = 'new' + filename
            filepath =  'media/media/' + request.FILES['document'].name
            filepath2 = 'media/media/' + 'new' + request.FILES['document'].name
            subprocess.run(["sox", '-v 0.75', filepath, filepath2, "rate", "16000"])
            fs = FileSystemStorage(location='media/media/')
            if fs.exists(filename):
                print(filename)
                try:
                    readaudio = fs.open(filename2)
                except:
                    return HttpResponse("<h2>Opening the file after using sox didn't work.</h2>")
            stuff = request.FILES['document']
            json_out = post_upload(readaudio, filename2)
            if json_out == -1:
                return HttpResponse("<h2>The file sample rate does not adhere to Watson requirements.</h2>")
            json_outone = json_out[0]
            json_outtwo = json_out[1]
            json_outthree = json_out[2]
            #pdb.set_trace()
            return render(request, 'upload/home.html', {
                'json_out': json_out,
                'json_outone': json_out[0],
                'json_outtwo': json_out[1],
                'json_outthree': json_out[2],
                'filename': filename, 
                }) 
    else:
        form = DocumentForm()
    return render(request, 'about/home.html', {
       'form': form
        })

def post_upload(f, filename):
    #pdb.set_trace()
    print(filename)
    ext = filename.split(".")[-1]
    #determining what file type upload is
    if ext == "wav":
        try:
            thej = json.dumps(stt.recognize(f, timestamps=True, content_type="audio/wav", continuous=True, inactivity_timeout=None), indent=2)
        except:
            return -1
    elif ext == "flac":
        try:
            thej = json.dumps(stt.recognize(f, timestamps=True, content_type="audio/flac", continuous=True, inactivity_timeout=None), indent=2)
        except WatsonException(error_message):
            return HttpResponse("<h2>Error returned from Watson's STT on given flac file.</h2>")
    elif ext == "ogg":
        try:
            thej = json.dumps(stt.recognize(f, timestamps=True, content_type="audio/ogg", continuous=True, inactivity_timeout=None), indent=2)
        except WatsonException(error_message):
            return HttpResponse("<h2>Error returned fromm Watson's STT on given flac file.</h2>")
    else:
        return HttpResponse("<h2>File format submitted did not appear to be wav, flac, or ogg...</h2>")
    return extract_json(thej)
      
def extract_json(j):
    data = json.loads(j)
    word_index = data["results"][0]["alternatives"][0]["timestamps"]
    # The *full* transcript. Currently has strange formating with pprint.
    transcript = data["results"][0]["alternatives"][0]["transcript"]
    # The confidence level between 0.000 and 1.000
    confidence = data["results"][0]["alternatives"][0]["confidence"]
    return(word_index)
