# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
        form = SalePaymentForm(request)
    return render(request, "payment/carddetails.html", {'form': form})
