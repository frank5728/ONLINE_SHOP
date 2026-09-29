from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings

from .models import Product, Size, Order
from google import genai


# ==============================
# HOME PAGE
# ==============================

def home(request):
    return render(request, "shop/home.html")


# ==============================
# SHOP PAGE
# ==============================

def shop_home(request):
    products = Product.objects.prefetch_related("sizes").all()

    return render(
        request,
        "shop/shop.html",
        {"products": products}
    )


# ==============================
# PRODUCT SIZES
# ==============================

def product_sizes(request):

    product_id = request.GET.get("product_id")

    if not product_id:
        return JsonResponse({"sizes": []})

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({"sizes": []})

    sizes = product.sizes.all()

    size_data = [
        {
            "id": size.id,
            "name": size.name
        }
        for size in sizes
    ]

    return JsonResponse({"sizes": size_data})


# ==============================
# CUSTOMER ORDER
# ==============================

def order(request):

    if request.method == "POST":

        customer_name = request.POST.get(
            "customer_name",
            ""
        ).strip()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        location = request.POST.get(
            "location",
            ""
        ).strip()

        product_id = request.POST.get("product_id")
        size_id = request.POST.get("size")

        quantity_text = request.POST.get(
            "quantity",
            "1"
        )

        if not customer_name:
            messages.error(
                request,
                "Please enter your name."
            )
            return redirect("order")

        if not phone:
            messages.error(
                request,
                "Please enter your phone number."
            )
            return redirect("order")

        if not location:
            messages.error(
                request,
                "Please enter your location."
            )
            return redirect("order")

        if not product_id:
            messages.error(
                request,
                "Please select a product."
            )
            return redirect("order")

        if not size_id:
            messages.error(
                request,
                "Please select a size."
            )
            return redirect("order")

        try:
            quantity = int(quantity_text)
        except (ValueError, TypeError):
            quantity = 0

        if quantity < 1:
            messages.error(
                request,
                "Quantity must be at least 1."
            )
            return redirect("order")

        product = get_object_or_404(
            Product,
            id=product_id
        )

        size = get_object_or_404(
            Size,
            id=size_id
        )

        if not product.sizes.filter(
            id=size.id
        ).exists():

            messages.error(
                request,
                "The selected size is not available for this product."
            )

            return redirect("order")

        total_price = product.price * quantity

        new_order = Order.objects.create(
            customer_name=customer_name,
            phone=phone,
            location=location,
            product=product,
            size=size,
            quantity=quantity,
            total_price=total_price,
            status="Pending"
        )

        messages.success(
            request,
            f"Order {new_order.order_reference} submitted successfully."
        )

        return redirect(
            "order_status",
            order_id=new_order.id
        )

    products = Product.objects.prefetch_related(
        "sizes"
    ).all()

    selected_product_id = request.GET.get(
        "product_id"
    )

    return render(
        request,
        "shop/order.html",
        {
            "products": products,
            "selected_product_id": selected_product_id
        }
    )


# ==============================
# ORDER STATUS
# ==============================

def order_status(request, order_id):

    order_obj = get_object_or_404(
        Order.objects.select_related(
            "product",
            "size"
        ),
        id=order_id
    )

    return render(
        request,
        "shop/order_status.html",
        {"order": order_obj}
    )


# ==============================
# CUSTOMER ORDERS
# ==============================

def my_orders(request):

    orders = Order.objects.select_related(
        "product",
        "size"
    ).order_by("-created_at")

    return render(
        request,
        "shop/my_orders.html",
        {"orders": orders}
    )


# ==============================
# CANCEL ORDER
# ==============================

def cancel_order(request, order_id):

    order_obj = get_object_or_404(
        Order,
        id=order_id
    )

    if request.method == "POST":

        order_obj.status = "Cancelled"

        order_obj.save(
            update_fields=["status"]
        )

        messages.success(
            request,
            "Order cancelled successfully."
        )

    return redirect(
        "order_status",
        order_id=order_id
    )


# ==============================
# CHATBOT PAGE
# ==============================

def chatbot(request):

    return render(
        request,
        "shop/chatbot.html"
    )


# ==============================
# CHATBOT API
# ==============================

def chatbot_api(request):

    # Only POST requests are allowed

    if request.method != "POST":

        return JsonResponse(
            {"response": "Invalid request."},
            status=400
        )

    # Get customer message

    user_message = request.POST.get(
        "message",
        ""
    ).strip()

    if not user_message:

        return JsonResponse({
            "response": "Please type your question."
        })

    message = user_message.lower()

    # ==============================
    # GET PRODUCTS
    # ==============================

    products = Product.objects.prefetch_related(
        "sizes"
    ).all()

    # ==============================
    # GREETINGS
    # ==============================

    greetings = [
        "habari",
        "hello",
        "hi",
        "hey",
        "mambo",
        "salama"
    ]

    if message in greetings:

        if message in ["hello", "hi", "hey"]:

            return JsonResponse({
                "response": (
                    "Hello! Welcome to our Online Shop. "
                    "How can I help you today?"
                )
            })

        return JsonResponse({
            "response": (
                "Habari! Karibu sana kwenye duka letu. "
                "Nawezaje kukusaidia leo?"
            )
        })

    # ==============================
    # SERVICES / HELP
    # ==============================

    service_words = [
        "huduma",
        "msaada",
        "service",
        "services",
        "help",
        "nahitaji huduma",
        "nataka huduma"
    ]

    if any(
        word in message
        for word in service_words
    ):

        if any(
            word in message
            for word in [
                "service",
                "services",
                "help"
            ]
        ):

            return JsonResponse({
                "response": (
                    "Hello! We can help you with "
                    "products, prices, sizes, "
                    "how to order, and payment."
                )
            })

        return JsonResponse({
            "response": (
                "Karibu! Tunaweza kukusaidia kuhusu "
                "bidhaa, bei, saizi, jinsi ya kuagiza "
                "na malipo."
            )
        })

    # ==============================
    # PAYMENT
    # ==============================

    payment_words = [
        "malipo",
        "lipa",
        "payment",
        "pay",
        "namba ya malipo",
        "namna ya kulipa"
    ]

    if any(
        word in message
        for word in payment_words
    ):

        if any(
            word in message
            for word in [
                "payment",
                "pay"
            ]
        ):

            return JsonResponse({
                "response": (
                    "Payment number: 0783707512\n"
                    "Payment name: "
                    "FRANK LUCAS MLYAKALAMU"
                )
            })

        return JsonResponse({
            "response": (
                "Namba ya malipo ni 0783707512.\n"
                "Jina la malipo ni "
                "FRANK LUCAS MLYAKALAMU."
            )
        })

    # ==============================
    # HOW TO ORDER
    # ==============================

    order_words = [
        "jinsi ya kuagiza",
        "naagizaje",
        "kuagiza",
        "order",
        "how to order",
        "how can i order",
        "how do i order"
    ]

    if any(
        word in message
        for word in order_words
    ):

        if any(
            word in message
            for word in [
                "how",
                "order"
            ]
        ):

            return JsonResponse({
                "response": (
                    "To order, select a product, "
                    "choose a size, enter your details, "
                    "select the quantity, and submit "
                    "your order."
                )
            })

        return JsonResponse({
            "response": (
                "Ili kuagiza, chagua bidhaa, "
                "chagua saizi, weka taarifa zako, "
                "chagua idadi ya bidhaa, kisha "
                "tuma oda yako."
            )
        })

    # ==============================
    # PRODUCT INFORMATION
    # ==============================

    product_words = [
        "bidhaa",
        "product",
        "products",
        "what do you sell",
        "what products",
        "kuna bidhaa",
        "kuna nini",
        "mnauza nini",
        "duka lina nini",
        "bidhaa gani"
    ]

    if any(
        word in message
        for word in product_words
    ):

        if not products:

            return JsonResponse({
                "response": (
                    "Samahani, kwa sasa hakuna "
                    "bidhaa zilizowekwa dukani."
                )
            })

        swahili_request = any(
            word in message
            for word in [
                "bidhaa",
                "kuna",
                "mnauza",
                "duka"
            ]
        )

        lines = []

        if swahili_request:

            lines.append(
                "Bidhaa zinazopatikana dukani ni:"
            )

        else:

            lines.append(
                "Available products in our shop:"
            )

        for product in products:

            sizes = [
                size.name
                for size in product.sizes.all()
            ]

            lines.append(
                f"- {product.name}: "
                f"{product.price:,.0f} TZS"
            )

            if sizes:

                if swahili_request:

                    lines.append(
                        f"  Saizi: {', '.join(sizes)}"
                    )

                else:

                    lines.append(
                        f"  Sizes: {', '.join(sizes)}"
                    )

        if swahili_request:

            lines.append(
                "\nUnaweza kuniuliza kuhusu "
                "bei, saizi au jinsi ya kuagiza."
            )

        else:

            lines.append(
                "\nYou can ask me about prices, "
                "sizes, or how to order."
            )

        return JsonResponse({
            "response": "\n".join(lines)
        })

    # ==============================
    # PRICE INFORMATION
    # ==============================

    price_words = [
        "bei",
        "price",
        "prices",
        "gharama",
        "how much",
        "how much is"
    ]

    if any(
        word in message
        for word in price_words
    ):

        if not products:

            return JsonResponse({
                "response": (
                    "Samahani, kwa sasa hakuna "
                    "bidhaa zilizowekwa dukani."
                )
            })

        english_request = any(
            word in message
            for word in [
                "price",
                "prices",
                "how much"
            ]
        )

        lines = []

        if english_request:

            lines.append(
                "Here are our current product prices:"
            )

        else:

            lines.append(
                "Hizi ni bei za bidhaa zilizopo:"
            )

        for product in products:

            lines.append(
                f"- {product.name}: "
                f"{product.price:,.0f} TZS"
            )

        return JsonResponse({
            "response": "\n".join(lines)
        })

    # ==============================
    # SIZE INFORMATION
    # ==============================

    size_words = [
        "size",
        "sizes",
        "saizi",
        "saizi gani",
        "ukubwa"
    ]

    if any(
        word in message
        for word in size_words
    ):

        if not products:

            return JsonResponse({
                "response": (
                    "Samahani, hakuna bidhaa "
                    "zilizopo kwa sasa."
                )
            })

        english_request = any(
            word in message
            for word in [
                "size",
                "sizes"
            ]
        )

        lines = []

        if english_request:

            lines.append(
                "Available sizes:"
            )

        else:

            lines.append(
                "Saizi zinazopatikana:"
            )

        for product in products:

            sizes = [
                size.name
                for size in product.sizes.all()
            ]

            if sizes:

                if english_request:

                    lines.append(
                        f"- {product.name}: "
                        f"{', '.join(sizes)}"
                    )

                else:

                    lines.append(
                        f"- {product.name}: "
                        f"{', '.join(sizes)}"
                    )

        if len(lines) == 1:

            lines.append(
                "Kwa sasa hakuna saizi zilizowekwa."
            )

        return JsonResponse({
            "response": "\n".join(lines)
        })

    # ==============================
    # GEMINI FOR OTHER QUESTIONS
    # ==============================

    api_key = getattr(
        settings,
        "GEMINI_API_KEY",
        None
    )

    if not api_key:

        return JsonResponse({
            "response": (
                "Samahani, huduma ya AI "
                "haipatikani kwa sasa."
            )
        })

    shop_information = []

    for product in products:

        sizes = [
            size.name
            for size in product.sizes.all()
        ]

        shop_information.append({
            "name": product.name,
            "price": str(product.price),
            "sizes": sizes
        })

    prompt = f"""
You are a customer service chatbot
for an online shop.

AVAILABLE PRODUCTS:
{shop_information}

PAYMENT NUMBER:
0783707512

PAYMENT NAME:
FRANK LUCAS MLYAKALAMU

CUSTOMER MESSAGE:
{user_message}

RULES:

1. Reply in the same language as the customer.

2. If the customer writes in Swahili,
   reply completely in Swahili.

3. If the customer writes in English,
   reply completely in English.

4. Do not unnecessarily mix languages.

5. Use only the available product information.

6. Never invent products, prices, sizes,
   discounts, delivery charges or payment details.

7. Be polite, friendly and concise.

8. If you do not know something,
   say so clearly.
"""

    try:

        client = genai.Client(
            api_key=api_key
        )

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        answer = response.text

        if answer and answer.strip():

            return JsonResponse({
                "response": answer.strip()
            })

        return JsonResponse({
            "response": (
                "Samahani, sijapata jibu kwa sasa. "
                "Tafadhali jaribu tena."
            )
        })

    except Exception as e:

        print(
            "CHATBOT ERROR:",
            e
        )

        return JsonResponse({
            "response": (
                "Samahani, huduma ya AI "
                "haipatikani kwa sasa. "
                "Tafadhali jaribu tena baadaye."
            )
        })