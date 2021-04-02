from django.forms import ModelForm, Form
from django import forms
from django.forms.widgets import CheckboxSelectMultiple, RadioSelect
from django.core.exceptions import ValidationError


MC_SET = {"A", "B", "C", "D"}
TF_SET = {"T", "F"}


class AssessmentAdminForm(ModelForm):
    """
    AssessmentAdminForm Allows us to override how the admin form behaves for validation.
    e.g. replace name field of bar with foo
    """

    def clean(self):
        # TODO: Remove me, no longer needed.
        # XXX: Calling super() just sets self._validate_unique = True
        super(ModelForm, self).clean()
        # Validate the number of questions selected are OK.
        # XXX: Not needed if admin widget does it.
        # if len(self.cleaned_data["questions"]) < 10:
        #    raise forms.ValidationError("You do not have at least 10 questions")
        return self.cleaned_data

    def clean_name(self):
        # TODO: Remove me, example.
        if self.cleaned_data["name"] == "bar":
            # Modify the name field if name is bar.
            self.cleaned_data["name"] = "foo"
            return self.cleaned_data["name"]
        return self.cleaned_data["name"]


class AssessmentResponseForm(Form):
    """
    Provides a non-ModelForm backed Form to collect and validate input from a user taking an Assessment.
    """

    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop("question", None)
        super(AssessmentResponseForm, self).__init__(*args, **kwargs)
        choice_list = [x for x in self.question.get_question_details()]
        if self.question.question_type() == "TF":
            self.fields["selection"] = forms.ChoiceField(
                choices=[("T", "True"), ("F", "False")], widget=RadioSelect
            )
        elif self.question.question_type() == "MC":
            self.fields["selection"] = forms.MultipleChoiceField(
                choices=choice_list, widget=CheckboxSelectMultiple
            )
        else:
            raise ValidationError("Question type not supported")

        self.fields["selection"].empty_label = None

    def clean_selection(self):
        # Is this a MC question?
        if isinstance(self.fields["selection"], forms.MultipleChoiceField):
            # Did we get a list.
            if isinstance(self.cleaned_data["selection"], list):
                # We can only have up to 4 values.
                if len(self.cleaned_data["selection"]) == 0:
                    return ValidationError("You must select at least one value")
                if len(self.cleaned_data["selection"]) > 4:
                    return ValidationError("Invalid number of selections")
                # Does the list contain the right values?
                for element in self.cleaned_data["selection"]:
                    if element in MC_SET:
                        pass
                    else:
                        return ValidationError(f"Found bad element: {element}")
                # It passes
                return self.cleaned_data["selection"]

        # Is this a TF question
        elif isinstance(self.fields["selection"], forms.ChoiceField):
            # Gave more than one value in TF question.
            if len(self.cleaned_data["selection"]) > 1:
                return ValidationError("To many values given")
            # Didn't give a value.
            if len(self.cleaned_data["selection"]) == 0:
                return ValidationError("No values provided to question")
            # Didn't Give True or False.
            if not self.cleaned_data["selection"] in TF_SET:
                return ValidationError("Didn't provide True or False")
        else:
            raise ValidationError("Question type not supported")
        # It passes
        return self.cleaned_data["selection"]
