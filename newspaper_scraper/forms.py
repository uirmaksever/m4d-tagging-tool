from django import forms
from django.forms import formset_factory
from .models import Article2, Tag
from dal import autocomplete

def convert_distinct():
    distinct_list = []
    model = Tag.objects.all()
    for i in model:
        distinct_list.append(i.category_turkish)
    distinct_list = list(set(distinct_list))
    a = 0
    distinct_tuple = []
    for i in distinct_list:
        distinct_tuple.append((i, i))
        a += 1
    print(distinct_tuple)
    return distinct_tuple


class TaggingForm(forms.ModelForm):
    categories = forms.ChoiceField(
        choices=convert_distinct(),
        widget= autocomplete.ModelSelect2(attrs={'class':'tagsform_category'})) #forms.widgets.Select(attrs={'class':'tagsform_category'}))

    class Meta:
        model = Article2
        fields = ("categories", "tags", )
        widgets = {
            "tags": autocomplete.ModelSelect2Multiple(
                url="tag-autocomplete",
                forward=["categories"],
                attrs={
                    # Set some placeholder
                    'data-placeholder': 'Please select tag.',
                    'class': 'tagsform_tag'
                }
            )
        }
