from django.shortcuts import redirect


class AddUserInstanceViewMixin(object):
    def form_valid(self, form):
        if 'pk' in self.kwargs or 'slug' in self.kwargs:
            instance = self.get_object()
            for key in form.cleaned_data:
                setattr(instance, key, form.cleaned_data[key])
            instance.save(user=self.request.user)
        else:
            instance = self.model(**form.cleaned_data)
            instance.save(user=self.request.user)
        return redirect(instance.get_absolute_url())
