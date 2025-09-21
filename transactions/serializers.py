from rest_framework import serializers
from .models import Transaction, Account, Category


class TransactionSerializer(serializers.ModelSerializer):
    date = serializers.DateField()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "t_type",
            "amount",
            "currency",
            "payment_method",
            "date",
            "account",
            "category",
            "note",
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs["context"]["request"].user if "context" in kwargs else None
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            self.fields["account"].queryset = Account.objects.filter(user=user)
            self.fields["category"].queryset = Category.objects.filter(user=user)


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "name", "initial_balance", "currency"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "type"]
