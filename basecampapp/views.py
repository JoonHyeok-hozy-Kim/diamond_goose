from django.shortcuts import render

# Create your views here.
def about_this_view(request):
    return render(request, 'basecampapp/about_this.html')
    # return render(request, 'accountapp/temp_welcome.html')