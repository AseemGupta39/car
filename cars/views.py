from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
from .models import Car
from .serializers import CarSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from rest_framework.permissions import AllowAny

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Car, CarImage
from .forms import CarForm

@login_required
def car_list_view(request):
    cars = Car.objects.filter(user=request.user)
    search_query = request.GET.get('search')
    if search_query:
        cars = cars.filter(
            title__icontains=search_query
        ) | cars.filter(
            description__icontains=search_query
        ) | cars.filter(
            tags__icontains=search_query
        )
    return render(request, 'car_list.html', {'cars': cars})

@login_required
def car_detail_view(request, pk):
    car = get_object_or_404(Car, pk=pk, user=request.user)
    return render(request, 'car_detail.html', {'car': car})

@login_required
def car_create_view(request):
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.user = request.user
            car.save()

            # Handle multiple image upload
            images = request.FILES.getlist('images')
            for image in images[:10]:  # Limit to 10 images
                CarImage.objects.create(car=car, image=image)

            return redirect('car-list')
    else:
        form = CarForm()
    return render(request, 'car_form.html', {'form': form})

@login_required
def car_update_view(request, pk):
    car = get_object_or_404(Car, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()

            # Handle image updates (optional - clear or add new images)
            if 'images' in request.FILES:
                CarImage.objects.filter(car=car).delete()  # Remove old images (optional)
                images = request.FILES.getlist('images')
                for image in images[:10]:  # Limit to 10 images
                    CarImage.objects.create(car=car, image=image)

            return redirect('car-detail', pk=car.pk)
    else:
        form = CarForm(instance=car)
    return render(request, 'car_form.html', {'form': form, 'car': car})

@login_required
def car_delete_view(request, pk):
    car = get_object_or_404(Car, pk=pk, user=request.user)
    if request.method == 'POST':
        car.delete()
        return redirect('car-list')
    return render(request, 'car_confirm_delete.html', {'car': car})


class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({"error": "Please provide both username and password"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_201_CREATED)
        except:
            return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class CarListCreateView(generics.ListCreateAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [permissions.IsAuthenticated]

    # def get_queryset(self):
    #     return Car.objects.filter(user=self.request.user)
    def get(self, request):
        form = CarForm()
        cars = Car.objects.filter(owner=request.user)  # Adjust filtering as needed
        return render(request, 'cars/car_list_create.html', {'form': form, 'cars': cars})

    def post(self, request):
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.owner = request.user  # Assuming you have an owner field
            car.save()

            # Save multiple images
            for file in request.FILES.getlist('images'):
                CarImage.objects.create(car=car, image=file)

            return redirect('car-list-create')
        return render(request, 'cars/car_list_create.html', {'form': form})
    
    def get_queryset(self):
        user = self.request.user
        queryset = Car.objects.filter(user=user)
        query = self.request.query_params.get('search', None)
        if query:
            queryset = queryset.filter(title__icontains=query) | queryset.filter(description__icontains=query) | queryset.filter(tags__icontains=query)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CarDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Car.objects.filter(user=self.request.user)



