# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.db import models

# Create your models here.
from django.db import models

import website.settings as settings
import stripe


class Sale(models.Model):
    def __init__(self, *args, **kwargs):
        super(Sale, self).__init__(*args, **kwargs)

        # bring in stripe, and get the api key from settings.py
        stripe.api_key = settings.PINAX_STRIPE_SECRET_KEY

        self.stripe = stripe

    # store the stripe charge id for this sale
    charge_id = models.CharField(max_length=32, default="stripe_id")
    user_name = models.CharField(max_length=255, default="username")
    email_id = models.EmailField(max_length=200, default="Enter Email")
    amount = models.IntegerField(default=00)
    emails_count = models.IntegerField(default=00)
    emails_balance_count = models.IntegerField(default=00)
    date_time = models.DateTimeField(default=datetime.now())

    # def __unicode__(scharge_idelf):
    #     return self.

    # stripe_id = models.CharField(max_length=255, default="Stripe id")
    # plan = models.CharField(max_length=50, default="plan")


    # you could also store other information about the sale
    # but I'll leave that to you!


    def charge(self, price_in_cents, number, exp_month, exp_year, username, user_email, cvc):
        """
        Takes a the price and credit card details: number, exp_month,
        exp_year, cvc.

        Returns a tuple: (Boolean, Class) where the boolean is if
        the charge was successful, and the class is response (or error)
        instance.
        """
        #
        # if self.charge_id:  # don't let this be charged twice!
        #     return False, Exception ce

        try:
            response = self.stripe.Charge.create(
                amount=price_in_cents,
                currency="usd",
                card={
                    "number": number,
                    "exp_month": exp_month,
                    "exp_year": exp_year,
                    "cvc": cvc,
                    "name": user_email,

                    #### it is recommended to include the address!
                    # "address_line1" : self.address1,
                    # "address_line2" : self.address2,
                    # "daddress_zip" : self.zip_code,
                    # "address_state" : self.state,
                },
                description='Thank you for your purchase!')

            self.charge_id = response.id
            self.user_name = username
            self.email_id = user_email
            self.amount = price_in_cents/100
            if self.amount == 19:
                self.emails_count = 350
                self.emails_balance_count = 350
            if self.amount == 39:
                self.emails_balance_count = 1000
                self.emails_count = 1000
            if self.amount == 89:
                self.emails_balance_count = 5000
                self.emails_count = 5000
            if self.amount == 139:
                self.emails_balance_count = 10000
                self.emails_count = 10000
            self.date_time = datetime.now()


        except self.stripe.CardError as ce:
            # charge failed
            return False, ce


        return True, response


# class PayTransactions(models.Model):
#     user_name = models.CharField(max_length=255)
#     email_id = models.EmailField(max_length=200)
#     sale_id = models.ForeignKey(Sale, on_delete=models.CASCADE)
#     amount = models.CharField(max_length=5)
#     date_time = models.DateTimeField()
#
#     def __unicode__(self):
#         return self.email_id
