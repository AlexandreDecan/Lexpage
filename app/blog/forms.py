from django import forms
from django.template.defaultfilters import truncatewords, striptags, truncatechars

from commons.templatetags.markup_markdown import blogpost_markdown
from helpers.regex import RE_URL, RE_HASHTAG
from .models import BlogPost

import re


def clean_tags(tagstr):
    """
    Take a string and returns a list of unique tags,
    in lowercase. Raise a forms.ValidationError if there is
    one tag with less than 2 chars. """
    re_tag = re.compile(r'^[\w\-]{2,}$', re.UNICODE)

    tags = [x.lower().strip() for x in tagstr.split()]
    new_tags = []
    for tag in tags:
        if len(tag) < 2:
            raise forms.ValidationError('Le tag "%s" est trop court, il doit au moins faire 2 caractères.' % tag)
        if re_tag.match(tag) is None:
            raise forms.ValidationError('Le tag "%s" contient des caractères non-autorisés.' % tag)
        if not (tag in new_tags):
            new_tags.append(tag)
    return new_tags


class SearchByTagsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields['tags'].widget.attrs.update({'class': 'tags_complete'})

    def clean_tags(self):
        tags = clean_tags(self.cleaned_data['tags'])
        return ' '.join(tags)

    class Meta:
        model = BlogPost
        fields = ['tags']


class QuickShareForm(forms.Form):
    content = forms.CharField(
        label='Contenu du partage rapide',
        widget=forms.Textarea(attrs={
            'class': 'quickshare-input',
            'rows': 2,
        }))

    def clean_content(self):
        data = self.cleaned_data['content']

        # Content must have at least one link
        if not re.search(RE_URL, data):
            raise forms.ValidationError('Le texte doit au moins contenir un lien.')

        # Remove newlines
        data = ' '.join(data.splitlines())

        data_without_markup = striptags(blogpost_markdown(re.sub(RE_URL, '', data)))

        # Set title
        self.cleaned_data['title'] = truncatechars(truncatewords(data_without_markup, 8), BlogPost._meta.get_field('title').max_length - 3)

        # Set tags
        tags = ' '.join(re.findall(RE_HASHTAG, data_without_markup) + ['quickshare'])
        self.cleaned_data['tags'] = clean_tags(tags)

        return data


class UserCreatePostForm(forms.ModelForm):
    ACTION_DELETE = -1
    ACTION_DRAFT = BlogPost.STATUS_DRAFT
    ACTION_SUBMIT = BlogPost.STATUS_SUBMITTED
    ACTION_APPROVE = BlogPost.STATUS_APPROVED
    ACTION_PUBLISH = BlogPost.STATUS_PUBLISHED

    ACTION_CHOICES = (
        (ACTION_DELETE, 'Supprimer'),
        (ACTION_DRAFT, 'Enregistrer dans mes brouillons'),
        (ACTION_SUBMIT, 'Soumettre aux modérateurs'),
        (ACTION_APPROVE, 'Valider pour publication'),
        (ACTION_PUBLISH, 'Publier directement')
    )

    priority = forms.ChoiceField(choices=BlogPost.PRIORITY_CHOICES, label='Priorité', initial=BlogPost.PRIORITY_NORMAL, required=True)
    action = forms.ChoiceField(choices=ACTION_CHOICES[1:3], label='Action', initial=ACTION_DRAFT, required=True)

    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields['tags'].widget.attrs.update({'class': 'tags_complete'})
        self.fields['abstract'].widget.attrs.update({'rows': 2})
        self.fields['abstract'].widget.attrs.update({'class': 'markup-input markup-input-markdown'})
        self.fields['text'].widget.attrs.update({'class': 'markup-input markup-input-markdown'})

    def clean_tags(self):
        tags = clean_tags(self.cleaned_data['tags'])
        return ' '.join(tags)

    def clean_action(self):
        return int(self.cleaned_data['action'])

    class Meta:
        model = BlogPost
        fields = ['title', 'tags', 'abstract', 'text', 'priority']


class StaffCreatePostForm(UserCreatePostForm):
    action = forms.ChoiceField(choices=UserCreatePostForm.ACTION_CHOICES[1:], label='Action', initial=UserCreatePostForm.ACTION_DRAFT, required=True)

    class Meta:
        model = BlogPost
        fields = UserCreatePostForm.Meta.fields + ['action']


class UserEditPostForm(UserCreatePostForm):
    action = forms.ChoiceField(choices=UserCreatePostForm.ACTION_CHOICES[:3], label='Action', initial=UserCreatePostForm.ACTION_DRAFT, required=True)

    class Meta:
        model = BlogPost
        fields = UserCreatePostForm.Meta.fields + ['action']


class StaffEditPostForm(UserEditPostForm):
    action = forms.ChoiceField(choices=UserCreatePostForm.ACTION_CHOICES, label='Action', initial=UserCreatePostForm.ACTION_APPROVE, required=True)
