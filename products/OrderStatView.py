from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Sum, F
from django.db.models.functions import TruncMonth
from datetime import datetime
from collections import defaultdict
from .models import Category, Product, ProductFormat, Order, OrderItem

@api_view(['GET'])
def order_statistics(request):
    # Filtrer les commandes par l'utilisateur connecté
    status_stats = Order.objects.filter(user=request.user).values('status').annotate(
        count=Count('id'),
        total_amount=Sum(F('items__quantity') * F('items__price_at_order'))
    )
    
    # Calcul du montant total des commandes pour cet utilisateur
    total_amount = Order.objects.filter(user=request.user).annotate(
        order_amount=Sum(F('items__quantity') * F('items__price_at_order'))
    ).aggregate(total=Sum('order_amount'))

    # Top 3 des produits les plus vendus pour cet utilisateur
    top_3_products = OrderItem.objects.filter(
        order__user=request.user
    ).values(
        'product_format__product__name',
        'product_format__taille',
        'product_format__couleur',
        'product_format__image'
    ).annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:3]

    return Response({
        'status_statistics': status_stats,
        'total_amount': total_amount['total'] if total_amount['total'] else 0,
        'top_3_products': top_3_products
    })

@api_view(['GET'])
def product_sales_ranking(request):
    # Classement de tous les produits par ventes pour cet utilisateur
    all_products_sales = OrderItem.objects.filter(
        order__user=request.user
    ).values(
        'product_format__product__name',
        'product_format__product__id',
        'product_format__taille',
        'product_format__couleur',
        'product_format__image'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('price_at_order'))
    ).order_by('-total_sold')

    return Response({
        'products_ranking': all_products_sales
    })

@api_view(['GET'])
def monthly_orders_evolution(request):
    # Évolution des commandes par mois pour cet utilisateur
    monthly_stats = Order.objects.filter(
        user=request.user
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        order_count=Count('id'),
        total_amount=Sum(F('items__quantity') * F('items__price_at_order'))
    ).order_by('month')

    # Organisation des données par mois
    evolution_data = [{
        'month': stat['month'].strftime('%Y-%m'),
        'order_count': stat['order_count'],
        'total_amount': stat['total_amount'] if stat['total_amount'] else 0
    } for stat in monthly_stats]

    return Response({
        'monthly_evolution': evolution_data
    })