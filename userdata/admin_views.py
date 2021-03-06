from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext as _


from wagtail.contrib.modeladmin.views import IndexView
from wagtail.admin import messages
from wagtail.snippets.views.snippets import get_snippet_edit_handler

from .forms import ManySafetyInstructionsForm
from .models import SafetyInstructionUserRelation, StaffUser
from userinput.models import RUBIONUser


class Project2NuclideIndexView( IndexView ):
    page_title = _('Nuclides in the isotope laboratory')



def add_safety_relation( request, usertype, uid, iid ):
    edit_handler_cls = get_snippet_edit_handler(SafetyInstructionUserRelation)
#    print ('Edit handler class is: {}'.format(edit_handler_cls))
#    print ('Edit handler class is: {}'.format(edit_handler_cls.__dict__))
#    edit_handler_cls.bind_to(model=SafetyInstructionUserRelation)
    form_cls = edit_handler_cls.get_form_class()#)
    initials = {
        'instruction' : iid
    }
    if usertype == 'ruser':
        initials['rubion_user'] = uid
    elif usertype == 'rstaff':
        initials['rubion_staff'] = uid

    instance = SafetyInstructionUserRelation()

    if request.method == 'POST':
        form = form_cls(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()

            messages.success(
                request,
                _('Safety instruction added.')
            )
            opts = SafetyInstructionUserRelation._meta
            return redirect(
                '/admin/%s/%s/' % (opts.app_label, 'staffusermodelproxy')
            )
                

        else:
            messages.error(request, _("The Safety Instruction could not be created due to errors."))
            edit_handler = edit_handler_cls(instance=instance, form=form)
    else:
        form = form_cls(instance=instance, initial=initials)
#        edit_handler_cls.bind_to(instance=instance, form=form)
        edit_handler = edit_handler_cls


    return render(request, 'userdata/admin/safetyinstruction/create.html', {
        'model_opts': SafetyInstructionUserRelation._meta,
        'edit_handler': edit_handler,
        'form': form,        
    })

def add_many_safety_relations( request ):

    rstaff = StaffUser.objects.all()

    userids = [ staff.user for staff in rstaff if staff.user is not None ]
    print(RUBIONUser.objects.all().count())
    rusers = RUBIONUser.objects.exclude(linked_user__in = userids)
    print (rusers.count())
    if request.method == 'POST':
        form = ManySafetyInstructionsForm(request.POST)
        if form.is_valid():
            for uid in form.cleaned_data['users']:
                si = SafetyInstructionUserRelation(
                    rubion_user_id = uid,
                    date = form.cleaned_data['date'],
                    instruction_id = form.cleaned_data['si']
                ).save()

            for uid in form.cleaned_data['staff']:
                si = SafetyInstructionUserRelation(
                    rubion_staff_id = uid,
                    date = form.cleaned_data['date'],
                    instruction_id = form.cleaned_data['si']
                ).save()
            messages.success(
                request,
                _('Safety instructions added.')
            )
            
            
    else:
        form = ManySafetyInstructionsForm()
 
    return render(request, 'userdata/admin/safetyinstruction/many.html', {
        'rusers': [],
        'rstaff': rstaff,
        'form': form
    })

        
