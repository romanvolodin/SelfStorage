from dateutil.relativedelta import relativedelta
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from boxes.forms import CalcRequestForm, OrderForm, ProlongationForm
from users.forms import CustomUserCreationForm, LoginForm
from coords.views import get_nearest_storage
from .models import Box, Storage, Order


def index(request):
    Storage.objects.fetch_with_coords()
    nearest_storage_id = get_nearest_storage(request)
    if not nearest_storage_id:
        nearest_storage_id = Storage.objects.order_by("?").first().id

    nearest_storage = Storage.objects.filter(id=nearest_storage_id)

    nearest_storage = nearest_storage.fetch_with_min_price()
    nearest_storage = nearest_storage.fetch_with_boxes_available_count()
    nearest_storage_item = storage_serialize(nearest_storage.first())
    context = {
        "nearest_storage": nearest_storage_item,
        "login_form": LoginForm(),
        "registration_form": CustomUserCreationForm(),
        "calc_request_form": CalcRequestForm(),
    }
    return render(request, "main.html", context)


def box_serialize(box):
    return {
        "floor": box.floor,
        "number": box.number,
        "volume": box.volume,
        "price": box.price,
        "is_occupied": box.is_occupied,
        "dimensions": box.dimensions,
        "id": box.id,
    }


def storage_serialize(storage):
    return {
        "id": storage.id,
        "city": storage.city,
        "address": storage.address,
        "max_box_count": storage.max_box_count,
        "boxes_available": storage.boxes_available,
        "min_price": storage.min_price,
        "feature": storage.feature,
        "contacts": storage.contacts,
        "description": storage.description,
        "route": storage.route,
        "preview_img": storage.imgs.first().image.url if storage.imgs.count() else None,
        "temperature": storage.temperature,
        "ceiling_height": storage.ceiling_height,
    }


def boxes(request, storage_id):

    try:
        selected_storage = Storage.objects.get(id=storage_id)
    except Storage.DoesNotExist:
        return redirect("boxes:storages")

    boxes = selected_storage.boxes.prefetch_related("orders").is_occupied_update()
    storage_boxes = [box_serialize(box) for box in boxes.filter(is_occupied=False)]
    boxes_to_3 = []
    boxes_to_10 = []
    boxes_from_10 = []
    for box in storage_boxes:
        if int(box["volume"]) < 3:
            boxes_to_3.append(box)
        elif int(box["volume"]) < 10:
            boxes_to_10.append(box)
        else:
            boxes_from_10.append(box)

    boxes_all = boxes_to_3 + boxes_to_10 + boxes_from_10

    boxes_items = {
        "to_3": boxes_to_3,
        "to_10": boxes_to_10,
        "from_10": boxes_from_10,
        "boxes_all": boxes_all,
    }

    storages = Storage.objects.fetch_with_min_price()
    storages = storages.fetch_with_boxes_available_count()

    storage_items = []
    for storage in storages:
        serialized_storage = storage_serialize(storage)
        storage_items.append(serialized_storage)
        if storage.id == storage_id:
            selected_storage_item = serialized_storage
            selected_storage_item["images"] = [
                image.image.url
                for image in storage.imgs.all()
                if image.image.url != serialized_storage["preview_img"]
            ]

    context = {
        "storage_boxes": boxes_items,
        "storages": storage_items,
        "selected_storage": selected_storage_item,
        "login_form": LoginForm(),
        "registration_form": CustomUserCreationForm(),
        "calc_request_form": CalcRequestForm(),
    }
    return render(request, "boxes.html", context)


def storages(request):
    storages = Storage.objects.fetch_with_min_price()
    storages = storages.fetch_with_boxes_available_count()
    storage_items = [storage_serialize(storage) for storage in storages]

    context = {
        "storages": storage_items,
        "login_form": LoginForm(),
        "registration_form": CustomUserCreationForm(),
        "calc_request_form": CalcRequestForm(),
    }
    return render(request, "storages.html", context)


def handle_calc_request(request):
    if request.method == "POST":
        form = CalcRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "calc_request/success.html", {})
    else:
        form = CalcRequestForm()
    return render(request, "calc_request/form_page.html", {"calc_request_form": form})


def order_box(request, box_id):
    user = request.user
    if user.is_anonymous:
        return redirect(reverse("users:login"))

    selected_box = Box.objects.get(id=box_id)

    box_item = {
        "number": selected_box.number,
        "price": selected_box.price,
        "storage": selected_box.storage,
        "id": selected_box.id,
    }

    previous_orders = user.orders.filter(box=selected_box, payments__is_paid=True)

    if selected_box.is_occupied and not previous_orders:
        return HttpResponse("Коробка уже занята")

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            term = form.cleaned_data["term"]
            lease_start = form.cleaned_data["lease_start"]
            order.customer = user
            order.box = selected_box
            order.price = order.box.price * term
            order.lease_start = lease_start
            order.lease_end = lease_start + relativedelta(months=term)
            order.save()
            return render(
                request,
                "orders/create_order.html",
                {"form": form, "box": box_item, "order": order},
            )

        form = ProlongationForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            term = form.cleaned_data["term"]
            prolongation_start = previous_orders.first().lease_end
            order.customer = user
            order.box = selected_box
            order.price = order.box.price * term
            order.lease_start = prolongation_start
            order.lease_end = prolongation_start + relativedelta(months=term)
            order.save()
            return render(
                request,
                "orders/create_order.html",
                {"form": form, "box": box_item, "order": order},
            )
    else:
        if previous_orders:
            form = ProlongationForm()
            return render(
                request,
                "orders/create_order.html",
                {"form": form, "box": box_item, "order": None},
            )

        form = OrderForm()
        return render(
            request,
            "orders/create_order.html",
            {"form": form, "box": box_item, "order": None},
        )
