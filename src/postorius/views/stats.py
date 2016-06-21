import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import View
from postorius.auth.decorators import (
    list_owner_required, list_moderator_required)
from postorius.models import UnsubscriberStats,List
from postorius.forms import UnsubscriberStatsForm

@login_required
@list_owner_required
def stats(request,list_id):
    if request.method == 'POST':
        form = UnsubscriberStatsForm(request.POST)
        if form.is_valid():
            startdate = request.POST.get('start_date')
            enddate = request.POST.get('end_date')
            list_stats = UnsubscriberStats.objects.filter(list_id = list_id , date__range=[startdate, enddate]).order_by('-date')
            
            stats_member_mgt_page = list_stats.filter(channel = 'Member mgt page')
            stats_members_option_page = list_stats.filter(channel = 'Members option page')
            stats_admin_mass_unsubscription = list_stats.filter(channel = 'Admin mass Unsubscription')
            stats_disabled = list_stats.filter(channel = 'Disabled')

            return render(request , 'postorius/lists/stats.html', {'list_stats':list_stats, 'stats_member_mgt_page':stats_member_mgt_page, 'stats_members_option_page': stats_members_option_page, 'stats_admin_mass_unsubscription':stats_admin_mass_unsubscription, 'stats_disabled':stats_disabled})

    else:
        form = UnsubscriberStatsForm()
        list_id = list_id
        return render(request, 'postorius/lists/stats_form.html', {'form': form,'list_id':list_id})

class statsDeleteView(View):
    template_name = 'postorius/lists/delete_stats.html'
    def get(self,request,list_id):
       list_stats = UnsubscriberStats.objects.filter(list_id=list_id)
       list_stats.delete()

       return render(request , self.template_name)
