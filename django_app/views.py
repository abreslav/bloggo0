from django.shortcuts import render


def home(request):
    """
    Home page view that displays different content based on user authentication status.
    For authenticated users: displays the user's name
    For anonymous users: displays "You are not logged in" message
    """
    return render(request, 'home.html')
