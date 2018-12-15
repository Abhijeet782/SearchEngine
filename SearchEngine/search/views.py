from django.shortcuts import render
import urllib.request, urllib.error, requests
from django.shortcuts import HttpResponse
import urllib3
import pyrebase
from bs4 import BeautifulSoup

config = {
    'apiKey': "AIzaSyCn5sxR1Ag7DItushNS6_U_PtNcE8uYFOw",
    'authDomain': "django-project1234.firebaseapp.com",
    'databaseURL': "https://django-project1234.firebaseio.com",
    'projectId': "django-project1234",
    'storageBucket': "django-project1234.appspot.com",
    'messagingSenderId': "379390615731"
}
firebase = pyrebase.initialize_app(config)
DB = firebase.database()


# Create your views here.
def index(request):
    return render(request, 'search/index.html')


# <meta name="description" content="Create an account or log in to Facebook. Connect with friends, family and other people you know. Share photos and videos, send messages and get updates." />


def result(request):
    if request.method == 'POST':
        query = request.POST.get('search')
        query = query.lower()
        checkbox = request.POST.get('URL')
        header = {}
        header['User-Agent'] = "Mozilla/5.0 (X11; Linux i686)"

        if checkbox == 'on':
            data, value = urlOpener(query, header, request)

            # Correct URL
            if value == 1:
                return HttpResponse(data)
            # Incorrect URL
            else:
                return render(request, 'search/error.html', data)
        else:
            query=query.replace(".","_")
            data, searchValue = searchOpener(query, header, request)
            print("Hiiiiii",searchValue)
            if searchValue == 1:
                context=data
                return render(request, 'search/error.html', context)
            else:
                page_html=data
                return HttpResponse(page_html)


def extractFromMeta(page_html):
    page_html = BeautifulSoup(page_html)
    attr = {'name': 'keywords'}
    a = page_html.find('meta', attr)
    a = str(a)
    start = a.find('content=')
    start_keyword = a.find('"', start + 8)
    end_keyword = a.find('"', start_keyword + 1)
    keywords = a[start_keyword + 1:end_keyword]
    keywordsList = keywords.split(', ')
    return keywordsList


def error(request):
    render(request, 'search/error.html')


def urlOpener(query, header, request):
    try:

        req = urllib.request.Request("https://" + query + "/", headers=header)
        resp = urllib.request.urlopen(req)
        page_html = resp.read()
        keywordsList = extractFromMeta(page_html)
        urlList=query.split(".")
        domain=urlList[1]

        #Error here : Keyword checking again and again whenever runs
        #
        #
        #
        #
        #
        #
        ##
        #
        #
        #
        #
        #
        #


        keyPresent=DB.child("keyword").child(domain).child("keywords").get(keywordsList)
        DB.child("keyword").child(domain).child("keywords").set(keywordsList)
        keywordsToDatabase(keywordsList, query)
        return page_html, 1

    except urllib.error.URLError as e:
        print("Inside URL ERROR " + str(e.errno) + str(e.reason))
        context = {'error': e.reason}
        return context, 2


def searchOpener(query, header, request):
    print(query)
    url = DB.child(query[0]).child(query).get()
    print(url.val())
    print("I am here")
    if url.val() == None:
        context = {'error': " "}
        print("Wronggggggg")
        return context, 1
    else:
        print(url.val(), url.key())
        req = urllib.request.Request("https://" + str(url.val()) + "/", headers=header)
        resp =urllib.request.urlopen(req)
        page_html = resp.read()
        print("Correct")
        return page_html, 2


def keywordsToDatabase(keywordsList, query):

    for key in keywordsList:
        key = key.replace('.', '_')
        key = key.lower()
        url = DB.child(key[0]).child(key).get()
        print(url.key(), url.val())
        if url.val() is None:
            DB.child(key[0]).child(key).set(query)
        else:
            updating = {key[0]: str(url.val()) + ", " + query}
            # DB.child("Abhijeet").update(updating)
            DB.child(key[0]).update(updating)
            print("done updating")
