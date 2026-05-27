from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('', views.LoanListView.as_view(), name='list'),
    path('<int:pk>/', views.LoanDetailView.as_view(), name='detail'),
    path('issue/<int:book_pk>/', views.issue_book, name='issue_book'),
    path('return/<int:loan_pk>/', views.return_book, name='return_book'),
    path('my/', views.MyLoansView.as_view(), name='my_loans'),
    path('fines/', views.FineListView.as_view(), name='fine_list'),
    path('fines/<int:fine_pk>/pay/', views.pay_fine, name='pay_fine'),
]
