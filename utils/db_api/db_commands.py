from asgiref.sync import sync_to_async

from django.db.models import Q
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.telegrambot.telegrambot.settings')
import django

django.setup()
from django_project.telegrambot.usersmanage.models import User, UserMeetings, SettingModel


@sync_to_async
def select_user(telegram_id: int):
    user = User.objects.filter(telegram_id=telegram_id).values().first()
    return user


@sync_to_async
def add_user(telegram_id, name, username):
    return User(telegram_id=int(telegram_id), name=name, username=username).save()


@sync_to_async
def delete_user(telegram_id):
    return User.objects.filter(telegram_id=telegram_id).delete()


@sync_to_async
def delete_user_meetings(telegram_id):
    return UserMeetings.objects.filter(telegram_id=telegram_id).delete()


@sync_to_async
def add_meetings_user(telegram_id, username):
    return UserMeetings(telegram_id=int(telegram_id), username=username).save()


@sync_to_async
def select_all_user_meetings():
    users = UserMeetings.objects.all().values()
    return users


@sync_to_async
def select_user_meetings(telegram_id: int):
    user = UserMeetings.objects.filter(telegram_id=telegram_id).values().first()
    return user


@sync_to_async
def select_all_users():
    users = User.objects.all().values()
    return users


@sync_to_async
def select_all_users_id(telegram_id: int):
    users = User.objects.filter(telegram_id=telegram_id).all().values()
    return users


@sync_to_async
def count_users():
    return User.objects.all().count()


@sync_to_async
def update_user_data(telegram_id, **kwargs):
    return User.objects.filter(telegram_id=telegram_id).update(**kwargs)


@sync_to_async
def update_user_meetings_data(telegram_id, **kwargs):
    return UserMeetings.objects.filter(telegram_id=telegram_id).update(**kwargs)


@sync_to_async
def select_meetings_user(telegram_id: int):
    user = UserMeetings.objects.filter(telegram_id=telegram_id).values().first()
    return user


@sync_to_async
def select_user_username(username: str):
    user = User.objects.filter(username=username).values().first()
    return user


@sync_to_async
def search_users(need_partner_sex, need_age_min, need_age_max, user_need_city):
    return User.objects.filter(
        Q(is_banned=False) &
        Q(sex=need_partner_sex) &
        (Q(age__gte=need_age_min) & Q(age__lte=need_age_max) | Q(age__gte=need_age_min + 1) &
         Q(age__lte=need_age_max + 1)) &
        Q(city=user_need_city)).all().values()


@sync_to_async
def search_event_forms():
    return UserMeetings.objects.filter(Q(is_active=True) & Q(verification_status=True))


@sync_to_async
def search_users_all():
    return User.objects.filter(is_banned=False).all().values()


@sync_to_async
def count_all_users_kwarg(**kwarg):
    return User.objects.filter(**kwarg).all().values().count()


@sync_to_async
def update_setting(telegram_id: int, **kwargs):
    return SettingModel.objects.filter(telegram_id=telegram_id).update(**kwargs)


@sync_to_async
def select_setting(telegram_id):
    return SettingModel.objects.filter(telegram_id=telegram_id).values().first()


@sync_to_async
def add_user_to_settings(telegram_id: int):
    return SettingModel(telegram_id=int(telegram_id)).save()


@sync_to_async
def select_setting_tech_work():
    return SettingModel.objects.filter(technical_works=True).values().first()
