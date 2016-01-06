from django.http import HttpResponse, Http404

from django.core.urlresolvers import reverse_lazy

from django.views.generic import View, ListView, TemplateView, RedirectView
from django.views.generic.edit import FormView
from django.views.generic.dates import MonthArchiveView

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from notifications import notify

from .forms import UserCreatePostForm, StaffCreatePostForm, UserEditPostForm, StaffEditPostForm, SearchByTagsForm

from .models import BlogPost
from datetime import date

import json


class PostListView(MonthArchiveView):
    """
    Provide a monthly-based archive view.
    """
    queryset = BlogPost.published.all()
    date_field = 'date_published'
    make_object_list = True
    allow_empty = True
    template_name = 'blog/list.html'
    context_object_name = 'post_list'

    def get_context_data(self, **kwargs):
        context = MonthArchiveView.get_context_data(self, **kwargs)
        context['date_list'] = PostListView.queryset.dates('date_published', 'month')
        context['date_current'] = date(int(self.get_year()), int(self.get_month()), 1)
        return context


class PostShowView(TemplateView):
    """
    Provide a view for a single object.
    """
    template_name = 'blog/show.html'

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        context['post'] = get_object_or_404(BlogPost.published, pk=kwargs['pk'])
        return context


class PostCommentsView(RedirectView):
    """
    Redirect to the right view:
     - "Show post" if there's already a comment on it;
     - "Post comment" otherwise.
    """
    permanent = False

    def get_redirect_url(self, **kwargs):
        post = get_object_or_404(BlogPost.published, pk=kwargs['pk'])
        try:
            return reverse_lazy('board_thread_show',
                                kwargs={'thread': post.blogboardlink.thread.pk, 'slug': post.blogboardlink.thread.slug})
        except ObjectDoesNotExist:
            return reverse_lazy('board_create_for_post', kwargs={'post': post.pk})


class DraftPostListView(ListView):
    """
    Provide a list of drafts for the current user.
    """
    template_name = 'blog/draft_list.html'
    context_object_name = 'post_list'

    dispatch = method_decorator(login_required)(ListView.dispatch)

    def get_queryset(self):
        return BlogPost.drafts.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = ListView.get_context_data(self, **kwargs)
        context['pending_list'] = BlogPost.submitted.filter(author=self.request.user) | BlogPost.approved.filter(
            author=self.request.user)
        return context


def _handle_status(request, post, action):
    """
    Shortcut function that provide a quick and dirty way to update
    the status of a post based on a given action. Notice that most of the
    logical behavior is in Post.change_status().

    This function also displays a success message to the user AND
    send a notification through the system (see Notification.notify).
    """

    # Clean the notifications if post.pk exists, ie. if it is already saved
    # in the database and thus, if it has already generated notifications.
    if post.pk is not None:
        notify.blog_pending_clean(request.user, post)

    if action == UserCreatePostForm.ACTION_DELETE:
        notify.blog_pending_delete(request.user, post)
        post.delete()
        messages.success(request, 'Le billet a été supprimé définitivement.')
    elif action == UserCreatePostForm.ACTION_DRAFT:
        post.change_status(request.user, BlogPost.STATUS_DRAFT)
        messages.success(request, 'Le billet a été sauvegardé dans vos brouillons.')
    elif action == UserCreatePostForm.ACTION_SUBMIT:
        post.change_status(request.user, BlogPost.STATUS_SUBMITTED)
        notify.blog_pending_new(request.user, post)
        messages.success(request, 'Le billet va être soumis aux modérateurs.')
    elif action == UserCreatePostForm.ACTION_APPROVE:
        post.change_status(request.user, BlogPost.STATUS_APPROVED)
        # Only notify if the post wasn't yet accepted
        if post.status != BlogPost.STATUS_APPROVED:
            notify.blog_pending_approve(request.user, post)
        messages.success(request, 'Le billet a été approuvé pour la publication.')
    elif action == UserCreatePostForm.ACTION_PUBLISH:
        post.change_status(request.user, BlogPost.STATUS_PUBLISHED)
        messages.success(request, 'Le billet est maintenant publié.')
    else:
        messages.warning(request, 'Action invalide sur ce billet.')


class PostCreateView(FormView):
    """
    Provide a form that can be used to create a new post.
    Notice that this view can receive a pair title/url by GET.
    """
    template_name = 'blog/draft_create.html'
    form_class = UserCreatePostForm
    success_url = reverse_lazy('blog_draft_list')

    dispatch = method_decorator(login_required)(FormView.dispatch)

    def get_form(self, form_class=None):
        # Use another form if the user has permission.
        if self.request.user.has_perm('blog.can_approve'):
            form_class = StaffCreatePostForm
        return FormView.get_form(self, form_class)

    def get_initial(self):
        initial = {}
        # Check for title/url in GET, and populate the form accordingly
        if 'title' in self.request.GET and 'url' in self.request.GET:
            initial['title'] = self.request.GET['title']
            link = '[%s](%s)' % (self.request.GET['title'], self.request.GET['url'])
            initial['abstract'] = link
        return initial

    def form_valid(self, form):
        data = form.cleaned_data
        post = BlogPost(title=data['title'],
                        author=self.request.user,
                        tags=data['tags'],
                        abstract=data['abstract'],
                        text=data['text'],
                        priority=data['priority'])
        _handle_status(self.request, post, data['action'])
        post.save()
        return FormView.form_valid(self, form)


class PostEditView(FormView):
    """
    General view that provide a form to modify a post.
    """
    template_name = 'blog/post_edit.html'
    form_class = UserEditPostForm
    success_url = None

    dispatch = method_decorator(login_required)(FormView.dispatch)

    def get_success_url(self):
        # Yeah, I know that blog_post_show will fail if current status is
        # not PUBLISHED...
        return reverse_lazy('blog_post_show', kwargs={'pk': self.kwargs['pk']})

    def get_initial(self):
        # Raise 404 if post does not exist
        post = get_object_or_404(BlogPost, pk=self.kwargs['pk'])
        if not post.can_be_viewed_by(self.request.user):
            # Raise 404, do not expose that this id exists with 403
            raise Http404

        return {
            'title': post.title,
            'tags': post.tags,
            'abstract': post.abstract,
            'text': post.text,
            'priority': post.priority,
            'action': post.status
        }

    def get_context_data(self, *args, **kwargs):
        context = FormView.get_context_data(self, *args, **kwargs)
        context['post'] = BlogPost.objects.get(pk=self.kwargs['pk'])
        return context

    def get_form(self, form_class=None):
        # Change the form if user has permission...
        if self.request.user.has_perm('blog.can_approve'):
            form_class = StaffEditPostForm
        return FormView.get_form(self, form_class)

    def form_valid(self, form):
        # Raise 404 if post does not exist
        post = get_object_or_404(BlogPost, pk=self.kwargs['pk'])
        if not post.can_be_viewed_by(self.request.user):
            # Raise 404, do not expose that this id exists with 403
            raise Http404

        data = form.cleaned_data
        post = BlogPost.objects.get(pk=self.kwargs['pk'])
        post.title = data['title']
        post.tags = data['tags']
        post.abstract = data['abstract']
        post.text = data['text']
        post.priority = data['priority']
        _handle_status(self.request, post, data['action'])

        return FormView.form_valid(self, form)


class DraftPostEditView(PostEditView):
    """
    Provide a form to edit a post, in the case of a draft.
    """
    template_name = 'blog/draft_edit.html'
    success_url = None

    def get_success_url(self):
        return reverse_lazy('blog_draft_list')


class PendingPostListView(TemplateView):
    """
    Provide a list of posts for the staff.
    """
    template_name = 'blog/pending_list.html'

    dispatch = method_decorator(login_required)(TemplateView.dispatch)

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        context['post_submitted'] = BlogPost.submitted.all()
        context['post_approved'] = BlogPost.approved.all()
        return context


class PendingPostEditView(PostEditView):
    """
    Provide a form to edit a post, in the case of a pending post.
    """
    template_name = 'blog/pending_edit.html'
    success_url = None

    def get_success_url(self):
        return reverse_lazy('blog_pending_list')


class TagListView(ListView):
    """
    Provide a list of tags that can be used to filter the list of
    posts. Notice that this view also provides a list of posts accordingly.
    """
    template_name = 'blog/list_tags.html'
    context_object_name = 'post_list'
    paginate_by = 10
    paginate_orphans = 2
    allow_empty = True
    queryset = None

    def get_queryset(self):
        queryset = BlogPost.published.all()
        for tag in self.searched_tags:
            # Will fail with SQLite!!
            queryset = queryset.filter(tags__iregex='[[:<:]]%s[[:>:]]' % tag.lower())

        return queryset

    def get_context_data(self, **kwargs):
        context = ListView.get_context_data(self, **kwargs)
        # context now has a key 'post_list' with the right queryset

        context['tag_list'] = BlogPost.published.get_tags_list(sort_name=True, relative=True)
        context['post_number'] = sum([x[1] for x in context['tag_list']])
        context['searched_tags'] = self.searched_tags
        context['searched_tags_raw'] = '+'.join(self.searched_tags)

        context['form'] = self.form
        return context

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if self.kwargs['taglist']:
            self.searched_tags = self.kwargs['taglist'].split('+')
        else:
            self.searched_tags = []

        # Form handling
        if request.method == 'POST':
            form = SearchByTagsForm(request.POST)
            if form.is_valid():
                new_searched_tags = form.cleaned_data['tags'].replace(' ', '+')
                return redirect(reverse_lazy('blog_tags', kwargs={'taglist': new_searched_tags}))
            else:
                self.form = form
        else:
            # Prepopulate form with current tags
            self.form = SearchByTagsForm({'tags': ' '.join(self.searched_tags)})
        return ListView.dispatch(self, request, *args, **kwargs)


