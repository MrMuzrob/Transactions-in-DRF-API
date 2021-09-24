from rest_framework.response import Response
from api.reports import transaction_report
from api.pagination import CustomPagination
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminOrReadOnly
from rest_framework.decorators import api_view
from .models import Category, Currency, Transaction
from .serializers import (
    CategorySerializer, 
    CurrencySerializer, 
    ReadTransactionSerialiezer,
    ReportParamsSerializer, 
    WriteTransactionSerialiezer,
    ReportEntrySerializer
    )

# Create your views here.


@api_view(['GET'])
def apiOverView(request):
    api_urls = {
        'Login':'login/',
        'Registration':'registration/',
        'Categories':'/categories/',
        'Transactions':'/transactions/',
        'Currencies':'/currencies/'
    }

    return Response(api_urls)

class CurrencyModelViewSet(ModelViewSet):
    permission_classes = (IsAdminOrReadOnly, )
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

class CategoryModelViewSet(ModelViewSet):
    permission_classes = (IsAdminOrReadOnly )
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

class TransactionModelViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, )
    pagination_class = CustomPagination
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('description',)
    ordering_filters = ("amount", "date")
    filterset_fields = ('currency__code',)

    def get_queryset(self):
        return Transaction.objects.select_related("currency", "category", "user").filter(user=self.request.user)
     

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ReadTransactionSerialiezer
        return WriteTransactionSerialiezer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)    


class TransactionReportAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        params_serializer = ReportParamsSerializer(data=request.GET, context={"request":request})
        params_serializer.is_valid(raise_exception=True)
        params = params_serializer.save()

        data = transaction_report(params)
        serializer = ReportEntrySerializer(instance=data, many=True)
        return Response(data=serializer.data)

        