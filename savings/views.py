from datetime import date, timedelta
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import get_user_model

from .models import Account, Transaction, User, Profile
from .forms import QuickTransactionAdd, AddTransaction

User = get_user_model()
USER_PREFERENCE_ACCOUNT_TRANSACTIONS_DAYS = 100

def index(request):
    context = {
        'account_list': Account.objects.all()
    }
    return render(request, 'savings/index.html', context)

def account(request, account_id):
    accountObj = get_object_or_404(Account, id=account_id)
    transactions = get_transactions_to_show_in_account(account_id)
    context = {
        'account': accountObj,
        'transactions': transactions
    }
    return render(request, 'savings/account.html', context)

def transaction(request, transaction_id):
    transaction_object = get_object_or_404(Transaction, id=transaction_id)
    context = {
        'transaction': transaction_object
    }
    return render(request, 'savings/transaction.html', context)

def quick_add_transaction(request):
    # Assume submitted form, validate
    if request.method == 'POST':
        form = QuickTransactionAdd(request.POST)
        if form.is_valid():
            new_transaction = Transaction()
            # Put form values in new transaction
            new_transaction.account = form.cleaned_data['account']
            new_transaction.is_spending = form.cleaned_data['is_spending']
            new_transaction.amount = form.cleaned_data['amount']
            if form.cleaned_data['description']:
                new_transaction.description = form.cleaned_data['description']
            if form.cleaned_data['category']:
                new_transaction.category = form.cleaned_data['category']
            # Save changes and redirect
            new_transaction.save()
            messages.add_message(request, messages.SUCCESS, 'Successfully created transaction.', extra_tags='alert')
            # Redirect after successful form submit
            return HttpResponseRedirect(reverse('account', kwargs={ 'account_id': new_transaction.account.id }))
        else:
            messages.add_message(request, messages.ERROR, 'There was an error while creating the transaction.', extra_tags='alert')
            return HttpResponseRedirect(reverse('quick_add_transaction'))
        
    # Assume initial rendering
    else:
        # Get default account if authenticated user
        if request.user.is_authenticated:
            initial_account = request.user.profile.default_account
        else:
            # Get account the user was before entering form, if any
            if 'HTTP_REFERER' in request.META:
                referer_url = request.META['HTTP_REFERER']
                if '/account/' in referer_url:
                    initial_account = referer_url[(referer_url.rfind('/'))+1:]
            else:
                initial_account = None

        context = {
            'form': QuickTransactionAdd(initial={'account': initial_account}),
            'initial_account_id': initial_account,
            'initial_account_type': type(initial_account)
        }
        return render(request, 'savings/quick_add_transaction.html', context)
    
def add_transaction(request):
    # Assume submitted form, validate
    if request.method == 'POST':
        form = AddTransaction(request.POST)
        if form.is_valid():
            new_transaction = Transaction()
            # Put required form values in new transaction
            new_transaction.account = form.cleaned_data['account']
            new_transaction.is_spending = form.cleaned_data['is_spending']
            new_transaction.amount = form.cleaned_data['amount']
            new_transaction.date = form.cleaned_data['date']
            # now optional fields
            if form.cleaned_data['description']:
                new_transaction.description = form.cleaned_data['description']
            if form.cleaned_data['category']:
                new_transaction.category = form.cleaned_data['category']
            if form.cleaned_data['recurring']:
                new_transaction.recurring = form.cleaned_data['recurring']
                new_transaction.recurring = form.cleaned_data['repeat_date']
            # Save changes and redirect
            new_transaction.save()
            messages.add_message(request, messages.SUCCESS, 'Successfully created transaction.', extra_tags='alert')
            return HttpResponseRedirect(reverse('account', kwargs={ 'account_id': new_transaction.account.id }))
        else:
            messages.add_message(request, messages.ERROR, 'There was an error while creating the transaction.', extra_tags='alert')
            return HttpResponseRedirect(reverse('add_transaction'))

    # Assume initial rendering
    else:
        context = {
            'form': AddTransaction,
        }
        return render(request, 'savings/add_transaction.html', context)

def get_transactions_to_show_in_account(account_id):
    end_date = date.today()
    start_date = end_date - timedelta(days=USER_PREFERENCE_ACCOUNT_TRANSACTIONS_DAYS)
    transactions = []
    for iterator in range(0,USER_PREFERENCE_ACCOUNT_TRANSACTIONS_DAYS):
        current_date = end_date - timedelta(days=iterator)
        day_transactions = Transaction.objects.filter(account__id=account_id, date=current_date)
        sum_transactions = 0
        for transaction in day_transactions:
            sum_transactions += transaction.amount
        if day_transactions:
            transactions.append({
                'date': current_date,
                'transactions': day_transactions,
                'number_of_transactions': len(day_transactions),
                'sum_transactions': sum_transactions
            })
    return transactions