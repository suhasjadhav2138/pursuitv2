# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime, tzinfo
from django.shortcuts import render
from form import SalePaymentForm
from django.shortcuts import render_to_response, render
from django.http import HttpResponse
from django.template import RequestContext
from django.http import HttpResponseRedirect
from sales.models import Sale
from django.contrib.auth.decorators import login_required
from django.template.context_processors import csrf

# Create your views here.
@login_required
def charge(request):
    c = {}
    c.update(csrf(request))
    print "pppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp"
    if request.method == "POST":
        form = SalePaymentForm(request.user, request.POST)
        print request.POST, "oooooooooooooooooooo"

        if form.is_valid(): # charges the card
            print("done!!!!!")
            return HttpResponseRedirect('/profile/')

        else:
            return render(request, "payment/carddetails.html", {'form': form})


    else:
        form = SalePaymentForm(request)
        trans_date = Sale.objects.filter(user_name=request.user).last()
        if trans_date:
            print trans_date, datetime.now(), (trans_date.date_time).replace(tzinfo=None)
            diff_date = (datetime.now() - (trans_date.date_time).replace(tzinfo=None))
            print diff_date, "pppppppppp", diff_date.days
            if diff_date.days <= 30:
                print diff_date
                msg = "Payment Already Done!"
                return render(request, "login/profile.html", {'form': form, 'details': msg}, c)

    return render(request, "payment/carddetails.html", {'form': form})
