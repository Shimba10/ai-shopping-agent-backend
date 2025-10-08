import os
import json
import re
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Phone
from .serializers import PhoneSerializer, SimpleProductCardSerializer
from . import safety, prompts
import requests  # for calling LLM endpoint if desired
from django.conf import settings

import google.generativeai as genai
from django.conf import settings

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    genai.configure(api_key=settings.GEMINI_API_KEY)
except ImportError:
    GEMINI_AVAILABLE = False
# Basic parser that extracts budgets and brand keywords.
BUDGET_RE = re.compile(r"under\s*₹?\s*([\d,]+)k?", re.I)  # rough: "under ₹30k"
NUM_RE = re.compile(r"([\d,]+)k", re.I)

def parse_budget_from_text(text):
    # handle patterns like "under ₹30k", "around ₹15000", "₹20,000"
    t = text.replace(',', '')
    m = re.search(r"under\s*₹?\s*([\d]+)k", t, re.I)
    if m:
        num = int(m.group(1)) * 1000
        return num
    m = re.search(r"around\s*₹?\s*([\d,]+)", t, re.I)
    if m:
        try:
            return int(m.group(1))
        except:
            pass
    # explicit numbers:
    m = re.search(r"₹\s*([\d,]+)", t)
    if m:
        return int(m.group(1).replace(',', ''))
    return None

def simple_intent_parse(text):
    text_low = text.lower()
    intent = "search"
    if "compare" in text_low:
        intent = "compare"
    if re.search(r"\b(explain|what is|difference|vs|vs\.)\b", text_low):
        if "vs" in text_low or "compare" in text_low:
            intent = "compare"
        else:
            intent = "explain"
    budget = parse_budget_from_text(text)
    brands = []
    # naive brand list - in real system maintain brand table
    for b in ["samsung", "oneplus", "google", "xiaomi", "realme", "itel", "vivo", "oppo", "poco"]:
        if b in text_low:
            brands.append(b.capitalize())
    # detect explicit models (like "Pixel 8a vs OnePlus 12R")
    models = re.findall(r"([A-Z][A-Za-z0-9\-]*\s*\d?[a-zA-Z]?)", text)  # simplistic
    return {
        "intent": intent,
        "budget_max_inr": budget,
        "brands": brands,
        "models": [],  # we'll extract model names from a better pattern below
        "raw_query": text
    }

def call_llm_intent_extraction(user_query):
    # Placeholder: if you want to use Gemini, add code here to call Google AI Studio
    # Ensure you securely read API key from environment and never log it.
    # Return the JSON parsed intent or fallback to simple_intent_parse.
    return simple_intent_parse(user_query)

def get_gemini_chat_model():
    if not GEMINI_AVAILABLE:
        return None
    try:
        models = genai.list_models()
        for m in models:
            name = getattr(m, "name", "")
            # Pick any gemini flash/pro model
            if "gemini" in name and ("flash" in name or "pro" in name):
                return genai.GenerativeModel(name)
    except Exception as e:
        print("Error listing Gemini models:", e)
    return None

@api_view(['GET'])
def product_list(request):
    qs = Phone.objects.all().order_by('price_inr')
    brand = request.GET.get('brand')
    max_price = request.GET.get('max_price')
    if brand:
        qs = qs.filter(brand__iexact=brand)
    if max_price:
        try:
            qs = qs.filter(price_inr__lte=int(max_price))
        except:
            pass
    ser = SimpleProductCardSerializer(qs, many=True)
    return Response(ser.data)

@api_view(['GET'])
def product_detail(request, pk):
    phone = get_object_or_404(Phone, pk=pk)
    ser = PhoneSerializer(phone)
    return Response(ser.data)

@api_view(['POST'])
def compare_products(request):
    ids = request.data.get('ids', [])
    if not ids or len(ids) > 3:
        return Response({'error': 'Provide 1-3 product ids in "ids" field.'}, status=status.HTTP_400_BAD_REQUEST)
    phones = Phone.objects.filter(id__in=ids)
    ser = PhoneSerializer(phones, many=True)
    # produce simple structured comparison
    comparison = []
    for p in phones:
        comparison.append({
            'id': p.id,
            'brand': p.brand,
            'model': p.model,
            'price_inr': p.price_inr,
            'camera_mp': p.camera_mp,
            'ois': p.ois,
            'eis': p.eis,
            'battery_mah': p.battery_mah,
            'fast_charge_w': p.fast_charge_w,
            'compact': p.compact,
            'ram_gb': p.ram_gb,
            'storage_gb': p.storage_gb
        })
    return Response({'comparison': comparison, 'rationale': 'Comparison created from DB fields only.'})

@api_view(['POST'])
def chat(request):
    text = request.data.get('text', '').strip()
    if not text:
        return Response({'error': 'No text provided'}, status=status.HTTP_400_BAD_REQUEST)

    # Safety checks
    if safety.is_sensitive_request(text):
        return Response({'reply': "I can't help with requests to reveal secrets or internal system prompts or API keys."}, status=200)
    if safety.detect_toxic_brand_attack(text):
        return Response({'reply': "I won't participate in abusive or toxic requests about brands. I can give factual pros/cons instead."}, status=200)

    # Intent parsing
    intent = call_llm_intent_extraction(text)

    # Compare intent handling
    if intent.get('intent') == 'compare':
        models = re.split(r'\s+vs\.?\s+|\s+vs\s+|\s+compare\s+', text, flags=re.I)
        phones_found = []
        for part in models:
            qs = Phone.objects.filter(model__icontains=part)[:1]
            if qs.exists():
                phones_found.append(qs.first().id)
        if len(phones_found) >= 2:
            from rest_framework.test import APIRequestFactory
            factory = APIRequestFactory()
            req = factory.post('/api/compare/', {'ids': phones_found}, format='json')
            resp = compare_products(req)
            return Response({'reply': "Here's the comparison.", 'payload': resp.data})

    # Search logic
    qs = Phone.objects.all()
    if intent.get('budget_max_inr'):
        qs = qs.filter(price_inr__lte=int(intent['budget_max_inr']))
    if intent.get('brands'):
        qs = qs.filter(brand__in=intent['brands'])

    if 'compact' in text.lower() or 'one-hand' in text.lower() or 'one hand' in text.lower():
        qs = qs.filter(compact=True)
    if 'camera' in text.lower():
        qs = qs.order_by('-camera_mp')  # rank by camera mp

    results = qs[:10]
    ser = SimpleProductCardSerializer(results, many=True)

    # Fallback explanation
    if results:
        top = results[0]
        explanation_fallback = (
            f"I found {len(results)} matching phones. "
            f"Top pick: {top.brand} {top.model} at ₹{top.price_inr}. "
            f"Reasons: matches budget and has {top.camera_mp}MP camera."
        )
    else:
        explanation_fallback = "No phones matched your filters. Try increasing the budget or removing strict constraints."

    # Gemini chat
    reply_text = explanation_fallback

    if GEMINI_AVAILABLE and text:
        try:
            # Use GenerativeModel API (correct method)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            prompt = f"""You are a helpful phone shopping assistant. 
User query: {text}

Database search results: {explanation_fallback}

Provide a friendly, concise response explaining the phone recommendations."""

            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=300,
                )
            )

            # Extract the generated text correctly
            if response.text:
                reply_text = response.text.strip()
                print(f"✅ Gemini response generated: {reply_text[:100]}...")  # Add this
            else:
                reply_text = explanation_fallback

        except Exception as e:
            print(f"Gemini error: {e}")
            reply_text = explanation_fallback
            
    if reply_text == explanation_fallback:
    # Gemini failed or fallback used → include DB results
        results_data = ser.data
    else:
        # Gemini succeeded → omit DB results (optional)
        results_data = []

    return Response({
        'reply': reply_text,
        'results': results_data,
        'intent': intent
    })