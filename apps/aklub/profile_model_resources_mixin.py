# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError

from import_export import fields
from import_export.resources import ModelResource

from .models import (
    BankAccount, DonorPaymentChannel, Event, Preference,
    ProfileEmail, Telephone, UserBankAccount,
)


def get_preference_model_fields():
    """ Get Preference model fields """
    exclude_fields = ('id', 'user', 'administrative_unit')
    fields = Preference._meta.fields

    return [field.name for field in fields if field.name not in exclude_fields]


def dehydrate_base(self, profile):
    pass


def get_profile_model_resource_custom_fields():
    """ Get profile model resource custom fields """
    _fields = ['telephone', 'donor']
    _fields.extend(get_preference_model_fields())
    result = {}
    for field in _fields:
        result[field] = fields.Field()

    return result


def preference_model_dehydrate_decorator(field):
    def wrap(f):
        def wrapped_f(self, profile):
            if profile.pk:
                preference = profile.preference_set.filter(
                    administrative_unit=profile.administrated_units.first(),
                ).first()
                if preference:
                    return getattr(preference, field)
        return wrapped_f
    return wrap


def get_preference_model_custom_field_dehydrate_func():
    funcs = {}
    fields = get_preference_model_fields()
    for field in fields:
        func_name = 'dehydrate_{}'.format(field)
        funcs[func_name] = (preference_model_dehydrate_decorator(field=field))(dehydrate_base)

    return funcs


def new_objects_validations(check):
    errors = {}
    for key in check.keys():
        try:
            check[key].full_clean()
        except Exception as e:
            e.update_error_dict(errors)
    if errors:
        raise ValidationError(errors)


def import_obj(self, obj, data, dry_run):  # noqa
    check = {}
    # Call this method only in the ProfileResource model resource subclass
    if hasattr(self, '_set_child_model_field_value'):
        self._set_child_model_field_value(obj=obj, data=data)
    obj.save()
    if data.get('username') == "":
        data["username"] = None

    if data.get('telephone'):
        check['telephone'], _ = Telephone.objects.get_or_create(
            telephone=data['telephone'],
            user=obj,
            defaults={'is_primary': None},
        )
    if data.get("email"):
        check['email'], _ = ProfileEmail.objects.get_or_create(
            email=data["email"],
            user=obj,
            defaults={'is_primary': True},
        )

    if data.get("administrative_units"):
        if not obj.administrative_units.filter(id=data["administrative_units"]):
            obj.administrative_units.add(data["administrative_units"])
            obj.save()
        check['preference'], _ = Preference.objects.get_or_create(
            user=obj,
            administrative_unit=obj.administrative_units.get(id=data["administrative_units"]),
        )
        if data.get("newsletter_on") is not None:
            check['preference'].newsletter_on = data['newsletter_on']
        if data.get("call_on") is not None:
            check['preference'].call_on = data['call_on']
        if data.get("challenge_on") is not None:
            check['preference'].challenge_on = data['challenge_on']
        if data.get("letter_on") is not None:
            check['preference'].letter_on = data['letter_on']
        if data.get("send_mailing_lists") is not None:
            check['preference'].send_mailing_lists = data['send_mailing_lists']
        if data.get("public") is not None:
            check['preference'].public = data['public']

        check['preference'].save()

    if data.get('event') and data.get('bank_account') and data.get('donor') == 'x':
        SS = data.get('SS', None)
        try:
            check['bank_account'] = BankAccount.objects.get(bank_account_number=data['bank_account'])
            check['event'] = Event.objects.get(id=data['event'])
        except Exception as e:
            raise ValidationError(e)

        check['donors'], _ = DonorPaymentChannel.objects.get_or_create(
                user=obj,
                event=check['event'],
                defaults={'SS': SS, 'money_account': check['bank_account']},
            )
        if data.get('VS') != "" and _:
            check['donors'].VS = data.get('VS')

        check['donors'].money_account = check['bank_account']
        check['donors'].full_clean()
        check['donors'].save()

        if data.get('user_bank_account'):
            check['user_bank_account'], _ = UserBankAccount.objects.get_or_create(bank_account_number=data['user_bank_account'])
            check['donors'].user_bank_account = check['user_bank_account']
            check['donors'].save()

    new_objects_validations(check)

    return super(ModelResource, self).import_obj(obj, data, dry_run)


def dehydrate_telephone(self, profile):
    return profile.get_telephone()


def dehydrate_donor(self, profile):
    donor_list = []
    for donor in profile.userchannels.all():
        if donor:
            donor_list.append(f"VS:{donor.VS}\n")
            try:
                donor_list.append(f"event:{donor.event.name}\n")
            except AttributeError:
                donor_list.append('event:\n')
            try:
                donor_list.append(f"bank_accout:{donor.money_account.bank_account_number}\n")
            except AttributeError:
                donor_list.append('bank_accout:\n')
            try:
                donor_list.append(f"user_bank_account:{donor.user_bank_account.bank_account_number}\n")
            except AttributeError:
                donor_list.append(f"user_bank_account:\n")
            donor_list.append("\n")

    return "".join(tuple(donor_list))


def before_import_row(self, row, **kwargs):
    row['is_superuser'] = 0
    row['is_staff'] = 0
    row['email'] = row['email'].lower() if row.get('email') else ''


def import_field(self, field, obj, data, is_m2m=False):
    if field.attribute and field.column_name in data:  # and not getattr(obj, field.column_name):
        field.save(obj, data, is_m2m)


def get_profile_model_resource_mixin_class_body():
    body = {}
    body['import_obj'] = import_obj
    body['dehydrate_telephone'] = dehydrate_telephone
    body['dehydrate_donor'] = dehydrate_donor
    body['before_import_row'] = before_import_row
    body['import_field'] = import_field

    # Custom fields (dehydrate funcs)
    body.update(get_profile_model_resource_custom_fields())
    # Preference model dehydrate funcs
    body.update(get_preference_model_custom_field_dehydrate_func())

    return body


ProfileModelResourceMixin = type(
    'ProfileModelResourceMixin',
    (ModelResource,),
    get_profile_model_resource_mixin_class_body(),
)
