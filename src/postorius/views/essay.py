from django.shortcuts import render
from postorius.models import EssaySubscribe

def EssayList(request,list_id,email):
    list_essay = EssaySubscribe.objects.filter(list_id=list_id, email=email).order_by('-date')
    return render(request , 'postorius/lists/application.html', {'object':list_essay})
    
