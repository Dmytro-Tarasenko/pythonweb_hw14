from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import F
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import logout as dj_logout
from django.contrib.auth import login as dj_login
from django.urls import reverse_lazy

from .models import Author, Quote, Tag


# Create your views here.
def index(request):
    quotes = [{'quote': quote.quote,
               'author': quote.author,
               'tagslist': list(quote.tags.all()),
               'href_name': quote.author.fullname.replace(' ', '_')}
              for quote in Quote.objects.all()]
    return render(request=request,
                  template_name='app_quotes/index.html',
                  context={'quotes': quotes})


def authors(request):
    def make_brief(author: Author) -> str:
        return author.description[:100] + "..."

    authors = list(zip(Author.objects.all(),
                       list(map(make_brief, Author.objects.all())),
                       [author.fullname.replace(' ', '_')
                        for author in Author.objects.all()]
                       )
                   )
    return render(request=request,
                  template_name='app_quotes/authors.html',
                  context={'authors': authors})


def author_name(request, name: str):
    name = name.replace('_', ' ')
    author = Author.objects.filter(fullname=name).first()
    return render(request=request,
                  template_name='app_quotes/author_info.html',
                  context={'author': author})


@login_required(login_url='/login/')
def add_author(request):
    if request.method == "GET":
        return render(request=request,
                      template_name='app_quotes/addauthor.html',
                      context={})
    try:
        born_date = datetime.strptime(request.POST['born-date'],
                                      "%Y-%m-%d")
    except Exception as err:
        print(err)
        return render(request=request,
                      template_name='app_quotes/addauthor.html',
                      context={'msg': err})
    born_date_str = born_date.strftime("%B %d, %Y")
    new_author = Author(fullname=request.POST['fullname'],
                        born_location=request.POST['born-location'],
                        description=request.POST['description'],
                        born_date=born_date_str)
    candidate = Author.objects.filter(fullname=new_author.fullname).first()
    if candidate:
        return render(request=request,
                  template_name='app_quotes/addauthor.html',
                  context={'msg':
                               f"Author {candidate.fullname} already exists"})
    new_author.save()
    return redirect('app_quotes:author',
                    name=new_author.fullname.replace(' ', '_'))


@login_required(login_url='/login/')
def add_quote(request):
    def create_value(author: Author) -> str:
        return author.fullname.replace(' ', '_')

    authors_list = zip(
        map(create_value,
            Author.objects.order_by(F('fullname').asc(nulls_last=True))),
        Author.objects.order_by(F('fullname').asc(nulls_last=True))
    )

    if request.method == "GET":
        return render(request=request,
                      template_name='app_quotes/addquote.html',
                      context={'authors': authors_list})
    # POST handler
    if request.method == "POST":
        author_post = request.POST['fullname']
        tags_post = request.POST['tags']
        quote = request.POST['quote']

        tags_to_put = []
        for tag in tags_post.split(' '):
            res = Tag.objects.filter(tag=tag).first()
            if res is None:
                new_tag = Tag(tag=tag)
                new_tag.save()
                res = Tag.objects.filter(tag=tag).first()
            tags_to_put.append(res)

        author_to_put = Author.objects.filter(
            fullname=author_post.replace('_', ' ')
        ).first()
        if author_to_put is None:
            err = f"Author {author_post.replace('_', ' ')} not found"
            return render(request=request,
                          template_name='app_quotes/addquote.html',
                          context={'authors': authors_list,
                                   'msg': err})
        new_quote = Quote(author=author_to_put,
                          quote=quote)
        new_quote.save()
        for tag in tags_to_put:
            new_quote.tags.add(tag)
        return redirect('app_quotes:home')


def tags(request):
    tags_list = [tag for tag in
                 Tag.objects.order_by(F('tag')\
                                      .asc(nulls_last=True))
                 if tag.tag != ""]
    return render(request=request,
                  template_name='app_quotes/tags.html',
                  context={'tags': tags_list})


def quotes(request,
           tag: str):
    res = Quote.objects.filter(tags__tag=tag).all()
    quotes = [{'quote': quote.quote,
               'author': quote.author,
               'tagslist': list(quote.tags.all()),
               'href_name': quote.author.fullname.replace(' ', '_')}
              for quote in res]
    return render(request=request,
                  template_name='app_quotes/tagged-quotes.html',
                  context={'quotes': quotes,
                           'tag_name': tag})


def login(request):
    if request.user.is_authenticated:
        return redirect("app_quotes:home")
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'],
                            password=request.POST['password'])
        if user is None:
            print('user is None')
            return render(request=request,
                          template_name='app_quotes/login.html',
                          context={'err': "Invalid credentials"})
        dj_login(request, user)
        next_url = request.POST['next']
        if next_url == 'None':
            next_url = "app_quotes:home"
        return redirect(next_url)
    # GET method
    next_url = request.GET.get('next')
    return render(request=request,
                  template_name='app_quotes/login.html',
                  context={'next_url': next_url})


def logout(request):
    if request.user.is_authenticated:
        dj_logout(request)
        return redirect('app_quotes:home')
    return render(request=request,
                  template_name='app_quotes/index.html',
                  context={})


def register(request):
    if request.user.is_authenticated:
        return redirect("app_quotes:home")
    if request.method == 'POST':
        data_ = request.POST
        if data_['password'] == data_['password2']:
            try:
                user = User.objects.create_user(username=data_['username'],
                                                email=data_['email'],
                                                password=data_['password'])

            except Exception as e:
                return render(request=request,
                              template_name='app_quotes/register.html',
                              context={'msg': f"User {data_['username']}"
                                              f" already exists."})
            user.save()
            return redirect('app_quotes:login')

        return render(request=request,
                      template_name='app_quotes/register.html',
                      context={'msg': "Passwords do not match"})

    return render(request=request,
                  template_name='app_quotes/register.html',
                   context={})


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    html_email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('app_quotes:password_reset_done')
    success_message = "An email with instructions to reset your password has been sent to %(email)s."
    subject_template_name = 'users/password_reset_subject.txt'
