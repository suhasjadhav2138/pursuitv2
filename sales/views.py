# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from form import SalePaymentForm
from django.shortcuts import render_to_response, render
from django.http import HttpResponse
from django.template import RequestContext

from sales.models import Sale

from django.template.context_processors import csrf

# Create your views here.
def charge(request):
    c = {}
    c.update(csrf(request))
    print "pppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp"
    if request.method == "POST":
        form = SalePaymentForm(request.POST)

        if form.is_valid(): # charges the card
            print("done!!!!!")
            return render(request, "login/profile.html", {'form': form},c)
    else:
        form = SalePaymentForm()
    return render(request, "payment/carddetails.html", {'form': form})
