# -*- coding: utf-8 -*-

# Author: Petr Dlouhý <petr.dlouhy@auto-mat.cz>
#
# Copyright (C) 2015 o.s. Auto*Mat
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
from . import autocom, mailing, admin, filters
from .confirmation import makepdf
from .models import TerminalCondition, Condition, UserInCampaign, Communication, AutomaticCommunication, AccountStatements, Payment, UserProfile, MassCommunication, TaxConfirmation, Campaign
from PyPDF2 import PdfFileReader
from django.contrib import admin as django_admin
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core import mail
from django.core.files import File
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.test import TestCase, RequestFactory
from django_admin_smoke_tests import tests
from freezegun import freeze_time
import datetime
import io


class BaseTestCase(TestCase):
    def assertQuerysetEquals(self, qs1, qs2):
        def pk(o):
            return o.pk
        return self.assertEqual(
            list(sorted(qs1, key=pk)),
            list(sorted(qs2, key=pk))
        )

    def assertQueryEquals(self, q1, q2):
        return self.assertEqual(
            q1.__str__(),
            q2.__str__()
        )


@freeze_time("2010-1-1")
class ConditionsTests(BaseTestCase):
    """ Test conditions infrastructure and conditions in fixtures """
    maxDiff = None

    def test_date_condition(self):
        c = Condition.objects.create(operation="and")
        TerminalCondition.objects.create(
            variable="UserInCampaign.date_condition",
            value="datetime.2010-09-24 00:00",
            operation=">",
            condition=c,
        )
        self.assertQueryEquals(c.get_query(), Q(date_condition__gt=datetime.datetime(2010, 9, 24, 0, 0)))
        self.assertQueryEquals(c.condition_string(), "None(UserInCampaign.date_condition > datetime.2010-09-24 00:00)")

    def test_boolean_condition(self):
        c = Condition.objects.create(operation="or")
        TerminalCondition.objects.create(
            variable="UserInCampaign.boolean_condition",
            value="true",
            operation="=",
            condition=c,
        )
        self.assertQueryEquals(c.get_query(), Q(boolean_condition=True))
        self.assertQueryEquals(c.condition_string(), "None(UserInCampaign.boolean_condition = true)")

    def test_time_condition(self):
        c = Condition.objects.create(operation="or")
        TerminalCondition.objects.create(
            variable="UserInCampaign.time_condition",
            value="month_ago",
            operation="<",
            condition=c,
        )
        self.assertQueryEquals(c.get_query(), Q(time_condition__lt=datetime.datetime(2009, 12, 2, 0, 0)))
        self.assertQueryEquals(c.condition_string(), "None(UserInCampaign.time_condition < month_ago)")

    def test_text_condition(self):
        c = Condition.objects.create(operation="or")
        TerminalCondition.objects.create(
            variable="UserInCampaign.text_condition",
            value="asdf",
            operation="contains",
            condition=c,
        )
        self.assertQueryEquals(c.get_query(), Q(text_condition__contains="asdf"))
        self.assertQueryEquals(c.condition_string(), "None(UserInCampaign.text_condition contains asdf)")

    def test_text_icontains_condition(self):
        c = Condition.objects.create(operation="or")
        TerminalCondition.objects.create(
            variable="UserInCampaign.text_condition",
            value="asdf",
            operation="icontains",
            condition=c,
        )
        self.assertQueryEquals(c.get_query(), Q(text_condition__icontains="asdf"))
        self.assertQueryEquals(c.condition_string(), "None(UserInCampaign.text_condition icontains asdf)")

    def test_action_condition_equals(self):
        c = Condition.objects.create(operation="or")
        TerminalCondition.objects.create(
            variable="action",
            value="asdf",
            operation="=",
            condition=c,
        )
        self.assertQueryEquals(c.get_query(action="asdf"), Q())

    def test_action_condition_not_equals(self):
        c = Condition.objects.create(operation="or")
        TerminalCondition.objects.create(
            variable="action",
            value="asdf",
            operation="=",
            condition=c,
        )
        self.assertQueryEquals(c.get_query(), Q(pk__in=[]))
        self.assertQueryEquals(c.condition_string(), "None(action = asdf)")

    def test_blank_condition(self):
        c = Condition.objects.create(operation="and")
        TerminalCondition.objects.create(
            variable="UserInCampaign.regular_payments",
            value="true",
            operation="=",
            condition=c,
        )
        self.assertQueryEquals(c.get_query(), Q(regular_payments=True))
        self.assertQueryEquals(c.condition_string(), "None(UserInCampaign.regular_payments = true)")

    def test_combined_condition(self):
        c = Condition.objects.create(operation="and")
        TerminalCondition.objects.create(
            variable="UserInCampaign.time_condition",
            value="timedelta.5",
            operation=">=",
            condition=c,
        )
        TerminalCondition.objects.create(
            variable="UserInCampaign.days_ago_condition",
            value="days_ago.6",
            operation="!=",
            condition=c,
        )
        self.assertQueryEquals(c.get_query(), ~Q(days_ago_condition=datetime.datetime(2009, 12, 26, 0, 0)) & Q(time_condition__gte=datetime.timedelta(5)))
        self.assertQueryEquals(c.condition_string(), "None(UserInCampaign.days_ago_condition != days_ago.6 and UserInCampaign.time_condition >= timedelta.5)")

    def test_multiple_combined_conditions(self):
        c1 = Condition.objects.create(operation="and")
        c2 = Condition.objects.create(operation="nor")
        c2.conds.add(c1)
        TerminalCondition.objects.create(
            variable="UserInCampaign.time_condition",
            value="timedelta.5",
            operation=">=",
            condition=c1,
        )
        TerminalCondition.objects.create(
            variable="UserInCampaign.days_ago_condition",
            value="days_ago.6",
            operation="!=",
            condition=c1,
        )
        TerminalCondition.objects.create(
            variable="UserInCampaign.int_condition",
            value="5",
            operation="<=",
            condition=c2,
        )
        TerminalCondition.objects.create(
            variable="UserInCampaign.int_condition",
            value="4",
            operation="=",
            condition=c2,
        )
        test_query = ~((~Q(days_ago_condition=datetime.datetime(2009, 12, 26, 0, 0)) & Q(time_condition__gte=datetime.timedelta(5))) | Q(int_condition=4) | Q(int_condition__lte=5))
        self.assertQueryEquals(c2.get_query(), test_query)
        self.assertQueryEquals(
            c2.condition_string(),
            "not(None(None(UserInCampaign.days_ago_condition != days_ago.6 and UserInCampaign.time_condition >= timedelta.5) "
            "or UserInCampaign.int_condition = 4 or UserInCampaign.int_condition <= 5))"
        )


class ConfirmationTest(TestCase):
    def test_makepdf(self):
        output = io.BytesIO()
        makepdf(output, 'Test name', 'male', 'Test street', 'Test city', 2099, 999)
        pdf = PdfFileReader(output)
        pdf_string = pdf.pages[0].extractText()
        self.assertTrue('Test name' in pdf_string)
        self.assertTrue('Test street' in pdf_string)
        self.assertTrue('Test city' in pdf_string)
        self.assertTrue('2099' in pdf_string)
        self.assertTrue('999' in pdf_string)

    def test_makepdf_female(self):
        output = io.BytesIO()
        makepdf(output, 'Test name', 'female', 'Test street', 'Test city', 2099, 999)
        pdf = PdfFileReader(output)
        pdf_string = pdf.pages[0].extractText()
        self.assertTrue('Test name' in pdf_string)
        self.assertTrue('Test street' in pdf_string)
        self.assertTrue('Test city' in pdf_string)
        self.assertTrue('2099' in pdf_string)
        self.assertTrue('999' in pdf_string)


class AutocomTest(TestCase):
    def setUp(self):
        self.user = User.objects.create()
        self.userprofile = UserProfile.objects.create(sex='male', user=self.user)
        self.userincampaign = UserInCampaign.objects.create(userprofile=self.userprofile)
        c = Condition.objects.create(operation="nor")
        TerminalCondition.objects.create(
            variable="action",
            value="test-autocomm",
            operation="==",
            condition=c,
        )
        AutomaticCommunication.objects.create(
            condition=c,
            template="Vazen{y|a} {pane|pani} $addressment $regular_frequency testovací šablona",
            template_en="Dear {sir|miss} $addressment $regular_frequency test template",
            subject="Testovací komunikace",
            subject_en="Testing communication",
        )

    def test_autocom(self):
        autocom.check(action="test-autocomm")
        communication = Communication.objects.get(user=self.userincampaign)
        self.assertTrue("testovací šablona" in communication.summary)
        self.assertTrue("člene Klubu přátel Auto*Matu" in communication.summary)
        self.assertTrue("Vazeny pane" in communication.summary)

    def test_autocom_female(self):
        self.userprofile.sex = 'female'
        self.userprofile.save()
        autocom.check(action="test-autocomm")
        communication = Communication.objects.get(user=self.userincampaign)
        self.assertIn("testovací šablona", communication.summary)
        self.assertIn("členko Klubu přátel Auto*Matu", communication.summary)
        self.assertIn("Vazena pani", communication.summary)

    def test_autocom_unknown(self):
        self.userprofile.sex = 'unknown'
        self.userprofile.save()
        autocom.check(action="test-autocomm")
        communication = Communication.objects.get(user=self.userincampaign)
        self.assertIn("testovací šablona", communication.summary)
        self.assertIn("člene/členko Klubu přátel Auto*Matu", communication.summary)
        self.assertIn("Vazeny/a pane/pani", communication.summary)

    def test_autocom_addressment(self):
        self.user.userprofile.sex = 'male'
        self.user.userprofile.addressment = 'own addressment'
        self.user.userprofile.save()
        autocom.check(action="test-autocomm")
        communication = Communication.objects.get(user=self.userincampaign)
        self.assertIn("testovací šablona", communication.summary)
        self.assertIn("own addressment", communication.summary)
        self.assertIn("Vazeny pane", communication.summary)

    def test_autocom_en(self):
        self.user.userprofile.sex = 'unknown'
        self.user.userprofile.language = 'en'
        self.user.userprofile.save()
        autocom.check(action="test-autocomm")
        communication = Communication.objects.get(user=self.userincampaign)
        self.assertIn("test template", communication.summary)
        self.assertIn("member of the Auto*Mat friends club", communication.summary)
        self.assertIn("Dear sir", communication.summary)


class MailingTest(TestCase):
    def test_mailing(self):
        sending_user = User.objects.create(
            first_name="Testing",
            last_name="UserInCampaign",
            email="test@test.com",
        )
        c = AutomaticCommunication.objects.create(
            condition=Condition.objects.create(),
            template="Testing template",
            subject="Testing email",
            method="email",
        )
        mailing.send_mass_communication(c, ["fake_user"], sending_user, save=False)
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual(msg.recipients(), ['test@test.com'])
        self.assertEqual(msg.subject, 'Testing email')
        self.assertIn("Testing template", msg.body)


class AdminTest(tests.AdminSiteSmokeTest):
    fixtures = ['conditions', 'users']

    def post_request(self, post_data):
        request = self.factory.post('/', post_data)
        request.user = self.superuser
        request._dont_enforce_csrf_checks = True
        request.session = 'session'
        request._messages = FallbackStorage(request)
        return request

    @freeze_time("2017-5-1")
    def test_tax_confirmation_generate(self):
        model_admin = django_admin.site._registry[TaxConfirmation]
        request = self.post_request({})
        response = model_admin.generate(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/aklub/taxconfirmation/")
        self.assertEqual(TaxConfirmation.objects.get(user__id=2978, year=2016).amount, 350)
        self.assertEqual(request._messages._queued_messages[0].message, 'Generated 1 tax confirmations')

    @freeze_time("2015-5-1")
    def test_account_statement_changelist_post(self):
        model_admin = django_admin.site._registry[AccountStatements]
        request = self.get_request()
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 200)

        with open("apps/aklub/test_data/test_darujme.xls", "rb") as f:
            post_data = {
                '_save': 'Save',
                "type": "darujme",
                "date_from": "2010-10-01",
                "csv_file": f,
                'payment_set-TOTAL_FORMS': 0,
                'payment_set-INITIAL_FORMS': 0,
            }
            request = self.post_request(post_data)
            response = model_admin.add_view(request)
            self.assertEqual(response.status_code, 302)
            obj = AccountStatements.objects.get(date_from="2010-10-01")
            self.assertEqual(response.url, "/admin/aklub/accountstatements/")
            self.assertEqual(obj.payment_set.count(), 3)

            self.assertEqual(request._messages._queued_messages[0].message, 'Skipped payments: Testing User 1 (test.user1@email.cz)')
            self.assertEqual(
                request._messages._queued_messages[1].message,
                'The Výpis z účtu "<a href="/admin/aklub/accountstatements/%(id)s/change/">%(id)s (2015-05-01)</a>" was added successfully.' % {'id': obj.id}
            )

    def test_mass_comminication_changelist_post_send_mails(self):
        model_admin = django_admin.site._registry[MassCommunication]
        request = self.get_request()
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 200)

        post_data = {
            '_continue': 'send_mails',
            'name': 'test communication',
            "method": "email",
            'date': "2010-03-03",
            "subject": "Subject",
            "template": "Test template",
        }
        request = self.post_request(post_data)
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 302)
        obj = MassCommunication.objects.get(name="test communication")
        self.assertEqual(obj.subject, "Subject")
        self.assertEqual(response.url, "/admin/aklub/masscommunication/%s/change/" % obj.id)

    def test_mass_comminication_changelist_post(self):
        model_admin = django_admin.site._registry[MassCommunication]
        request = self.get_request()
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 200)

        from django.core.files.uploadedfile import SimpleUploadedFile
        attachment = SimpleUploadedFile("attachment.txt", b"attachment", content_type="text/plain")
        post_data = {
            '_continue': 'test_mail',
            'name': 'test communication',
            "method": "email",
            'date': "2010-03-03",
            "subject": "Subject",
            "attachment": attachment,
            "template": "Test template",
        }
        request = self.post_request(post_data)
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 302)
        obj = MassCommunication.objects.get(name="test communication")
        self.assertEqual(obj.subject, "Subject")
        self.assertEqual(response.url, "/admin/aklub/masscommunication/%s/change/" % obj.id)

    def test_automatic_comminication_changelist_post(self):
        model_admin = django_admin.site._registry[AutomaticCommunication]
        request = self.get_request()
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 200)

        post_data = {
            '_continue': 'test_mail',
            'name': 'test communication',
            'condition': 1,
            "method": "email",
            "subject": "Subject",
            "template": "Test template",
        }
        request = self.post_request(post_data)
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 302)
        obj = AutomaticCommunication.objects.get(name="test communication")
        self.assertEqual(obj.subject, "Subject")
        self.assertEqual(response.url, "/admin/aklub/automaticcommunication/%s/change/" % obj.id)

    def test_user_in_campaign_changelist_post(self):
        model_admin = django_admin.site._registry[UserInCampaign]
        request = self.get_request()
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 200)

        post_data = {
            '_continue': 'Save',
            'variable_symbol': 1234,
            'activity_points': 13,
            'registered_support_0': "2010-03-03",
            'registered_support_1': "12:35",
            'campaign': '1',
            'verified': 1,
            'communications-TOTAL_FORMS': 0,
            'communications-INITIAL_FORMS': 0,
            'payment_set-TOTAL_FORMS': 0,
            'payment_set-INITIAL_FORMS': 0,
        }
        request = self.post_request(post_data)
        response = model_admin.add_view(request)
        self.assertEqual(response.status_code, 302)
        userincampaign = UserInCampaign.objects.get(variable_symbol=1234)
        self.assertEqual(response.url, "/admin/aklub/userincampaign/%s/change/" % userincampaign.id)

        self.assertEqual(userincampaign.activity_points, 13)
        self.assertEqual(userincampaign.verified_by.username, 'testuser')


def print_response(response):
    with open("response.html", "w") as f:
        f.write(response.content.decode())


class ViewsTests(TestCase):
    fixtures = ['conditions', 'users', 'communications']

    def setUp(self):
        self.user = User.objects.create_superuser(
            username='admin', email='test_user@test_user.com', password='admin')
        self.client.force_login(self.user)

    regular_post_data = {
        'user-email': 'test@test.cz',
        'user-first_name': 'Testing',
        'user-last_name': 'User',
        'userprofile-telephone': 111222333,
        'userincampaign-regular_frequency': 'monthly',
        'userincampaign-regular_amount': '321',
    }

    def test_regular_existing_email(self):
        address = reverse('regular')
        regular_post_data = self.regular_post_data.copy()
        regular_post_data['user-email'] = 'test.user@email.cz'
        response = self.client.post(address, regular_post_data, follow=False)
        self.assertContains(
            response,
            'Jejda! Tenhle mail už známe, vypadá to, že se do Klubu přátel Auto*Matu neregistrujete poprvé. '
            'Vaší náklonnosti si vážíme, registraci ale není nutné opakovat... '
            'Poslali jsme Vám do mailu údaje potřebné k dalším příspěvkům i radu, kam se obrátit, pokud potřebujete ještě něco jiného.')

    def test_regular_dpnk(self):
        address = reverse('regular-dpnk')
        response = self.client.get(address)
        self.assertContains(response, '<input class=" form-control" id="id_user-first_name" maxlength="30" name="user-first_name" type="text" required />', html=True)

        response = self.client.post(address, self.regular_post_data, follow=True)
        self.assertContains(response, '<h5>Děkujeme!</h5>', html=True)

        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual(msg.recipients(), ['test@test.cz', 'kp@auto-mat.cz'])
        self.assertEqual(msg.subject, 'New user')
        self.assertEqual(msg.body, 'New user has been created Jméno: Testing Příjmení: User Ulice: Město: PSC:\nE-mail: test@test.cz Telefon: 111222333\n\n')

        self.assertEqual(User.objects.get(email="test@test.cz").get_full_name(), "Testing User")
        self.assertEqual(User.objects.get(email="test@test.cz").username, "test3")
        self.assertEqual(UserProfile.objects.get(user__email="test@test.cz").telephone, '111222333')
        self.assertEqual(UserInCampaign.objects.get(userprofile__user__email="test@test.cz").regular_amount, 321)

    def test_regular(self):
        address = reverse('regular')
        response = self.client.get(address)
        self.assertContains(response, '<input id="id_user-first_name" maxlength="30" name="user-first_name" type="text" required />', html=True)

        response = self.client.post(address, self.regular_post_data, follow=True)
        self.assertContains(response, '<h1>Děkujeme!</h1>', html=True)

        self.assertEqual(User.objects.get(email="test@test.cz").get_full_name(), "Testing User")
        self.assertEqual(User.objects.get(email="test@test.cz").username, "test3")
        self.assertEqual(UserProfile.objects.get(user__email="test@test.cz").telephone, '111222333')
        self.assertEqual(UserInCampaign.objects.get(userprofile__user__email="test@test.cz").regular_amount, 321)

    def test_regular_wp(self):
        address = reverse('regular-wp')
        response = self.client.get(address)
        self.assertContains(response, '<input class=" form-control" id="id_user-first_name" maxlength="30" name="user-first_name" type="text" required />', html=True)

        response = self.client.post(address, self.regular_post_data, follow=True)
        self.assertContains(response, '<h1>Děkujeme!</h1>', html=True)

        self.assertEqual(User.objects.get(email="test@test.cz").get_full_name(), "Testing User")
        self.assertEqual(User.objects.get(email="test@test.cz").username, "test3")
        self.assertEqual(UserProfile.objects.get(user__email="test@test.cz").telephone, '111222333')
        self.assertEqual(UserInCampaign.objects.get(userprofile__user__email="test@test.cz").regular_amount, 321)

    def test_onetime(self):
        address = reverse('onetime')
        response = self.client.get(address)
        self.assertContains(response, '<input id="id_0-first_name" maxlength="40" name="0-first_name" type="text" required />', html=True)

        post_data = {
            'one_time_payment_wizard-current_step': 0,
            '0-email': 'test@test.cz',
            '0-first_name': 'Testing',
            '0-last_name': 'User',
            '0-amount': '321',
        }
        response = self.client.post(address, post_data, follow=True)
        self.assertContains(response, '<input id="id_userprofile__1-title_before" maxlength="15" name="userprofile__1-title_before" type="text" />', html=True)

        post_data = {
            'one_time_payment_wizard-current_step': 1,
            'userincampaign__1-note': 'Note',
            'user__1-first_name': 'Testing',
            'user__1-last_name': 'User',
            'user__1-email': 'test@test.cz',
            'userprofile__1-title_before': 'Tit.',
            'userprofile__1-title_after': '',
            'userprofile__1-street': 'On Street 1',
            'userprofile__1-city': 'City',
            'userprofile__1-country': 'Country',
            'userprofile__1-zip_code': '100 00',
            'userprofile__1-language': 'cs',
            'userprofile__1-telephone': '+420123456789',
            'userprofile__1-wished_tax_confirmation': 'on',
            'userprofile__1-wished_information': 'on',
            'userprofile__1-public': 'on',
            'userprofile__1-note': 'asdf',
        }
        response = self.client.post(address, post_data, follow=True)
        self.assertContains(response, '<h1>Děkujeme!</h1>', html=True)

        self.assertEqual(User.objects.get(email="test@test.cz").get_full_name(), "Testing User")
        self.assertEqual(User.objects.get(email="test@test.cz").username, "test3")
        self.assertEqual(UserProfile.objects.get(user__email="test@test.cz").telephone, '+420123456789')
        self.assertEqual(UserInCampaign.objects.get(userprofile__user__email="test@test.cz").note, 'Note')

    def test_onetime_existing_email(self):
        address = reverse('onetime')
        response = self.client.get(address)
        self.assertContains(response, '<input id="id_0-first_name" maxlength="40" name="0-first_name" type="text" required />', html=True)

        post_data = {
            'one_time_payment_wizard-current_step': 0,
            '0-email': 'test.user@email.cz',
            '0-first_name': 'Testing',
            '0-last_name': 'User',
            '0-amount': '321',
        }
        response = self.client.post(address, post_data, follow=True)
        self.assertContains(response, '<option value="2978">Test User &lt;t***r@e***.cz&gt;</option>', html=True)

        post_data = {
            'one_time_payment_wizard-current_step': 2,
            '2-uid': 2978,
        }
        response = self.client.post(address, post_data, follow=True)
        self.assertContains(response, '<input id="id_4-vs_check" maxlength="40" name="4-vs_check" type="text" />', html=True)

        post_data = {
            'one_time_payment_wizard-current_step': 4,
            '4-vs_check': 120127010,
        }
        response = self.client.post(address, post_data, follow=True)
        self.assertContains(response, '<h1>Děkujeme!</h1>', html=True)


class SmokeViewsTestsLogon(TestCase):
    fixtures = ['conditions', 'users']

    def setUp(self):
        self.user = User.objects.create_superuser(
            username='admin', email='test_user@test_user.com', password='admin')
        self.client.force_login(self.user)

    def verify_views(self, views, status_code_map):
        for view in views:
            status_code = status_code_map[view] if view in status_code_map else 200
            address = view
            response = self.client.get(address, follow=True)
            filename = view.replace("/", "_")
            if response.status_code != status_code:
                with open("error_%s.html" % filename, "w") as f:
                    f.write(response.content.decode())
            self.assertEqual(response.status_code, status_code, "%s view failed, the failed page is saved to error_%s.html file." % (view, filename))

    views = [
        '/admin',
        reverse('onetime'),
        reverse('donators'),
        reverse('profiles'),
    ]

    def test_aklub_views(self):
        """
        test if the user pages work
        """
        status_code_map = {
        }

        self.verify_views(self.views, status_code_map)


@freeze_time("2016-5-1")
class ModelTests(TestCase):
    fixtures = ['conditions', 'users']

    def setUp(self):
        call_command('denorm_init')
        self.u = UserInCampaign.objects.get(pk=2979)
        self.u1 = UserInCampaign.objects.get(pk=2978)
        self.p = Payment.objects.get(pk=1)
        self.p1 = Payment.objects.get(pk=2)
        self.p2 = Payment.objects.get(pk=3)
        self.p1.BIC = 101
        self.p1.save()
        call_command('denorm_flush')
        self.u1 = UserInCampaign.objects.get(pk=2978)
        self.tax_confirmation = self.u1.make_tax_confirmation(2016)

    def test_payment_model(self):
        self.assertEqual(self.p.person_name(), 'User Test')

    def test_user_model(self):
        self.assertEqual(self.u.is_direct_dialogue(), False)
        self.assertEqual(self.u.last_payment_date(), None)
        self.assertEqual(self.u.last_payment_type(), None)
        self.assertEqual(self.u.requires_action(), False)
        self.assertEqual(self.u.expected_regular_payment_date, None)
        self.assertEqual(self.u.regular_payments_delay(), False)
        self.assertEqual(self.u.extra_payments(), '<img src="/media/admin/img/icon-no.svg" alt="False" />')
        self.assertEqual(self.u.no_upgrade, False)
        self.assertEqual(self.u.monthly_regular_amount(), 0)

        self.assertEqual(self.u1.is_direct_dialogue(), False)
        self.assertEqual(self.u1.person_name(), 'User Test')
        self.assertEqual(self.u1.requires_action(), True)
        self.assertListEqual(list(self.u1.payments()), [self.p1, self.p2, self.p])
        self.assertEqual(self.u1.number_of_payments, 3)
        self.assertEqual(self.u1.last_payment, self.p1)
        self.assertEqual(self.u1.last_payment_date(), datetime.date(2016, 3, 9))
        self.assertEqual(self.u1.last_payment_type(), 'bank-transfer')
        self.assertEqual(self.u1.regular_frequency_td(), datetime.timedelta(31))
        self.assertEqual(self.u1.expected_regular_payment_date, datetime.date(2016, 4, 9))
        self.assertEqual(self.u1.regular_payments_delay(), datetime.timedelta(12))
        self.assertEqual(self.u1.extra_money, None)
        self.assertEqual(self.u1.regular_payments_info(), datetime.date(2016, 4, 9))
        self.assertEqual(self.u1.extra_payments(), '<img src="/media/admin/img/icon-no.svg" alt="False" />')
        self.assertEqual(self.u1.mail_communications_count(), False)
        self.assertEqual(self.u1.payment_total, 350.0)
        self.assertEqual(self.u1.total_contrib_string(), "350&nbsp;Kč")
        self.assertEqual(self.u1.registered_support_date(), "16. 12. 2015")
        self.assertEqual(self.u1.payment_total_range(datetime.date(2016, 1, 1), datetime.date(2016, 2, 1)), 0)
        self.assertEqual(self.tax_confirmation.year, 2016)
        self.assertTrue("PDF-1.4" in str(self.tax_confirmation.file.read()))
        self.assertEqual(self.tax_confirmation.amount, 350)
        self.assertEqual(self.u1.no_upgrade, False)
        self.assertEqual(self.u1.monthly_regular_amount(), 100)

    def test_extra_payments(self):
        Payment.objects.create(date=datetime.date(year=2016, month=5, day=1), user=self.u1, amount=250)
        call_command('denorm_flush')
        self.u1 = UserInCampaign.objects.get(pk=2978)
        self.assertEqual(self.u1.extra_money, 150)
        self.assertEqual(self.u1.extra_payments(), "150&nbsp;Kč")


class AccountStatementTests(TestCase):
    fixtures = ['conditions', 'users']

    def test_bank_new_statement(self):
        with open("apps/aklub/test_data/Pohyby_5_2016.csv", "rb") as f:
            a = AccountStatements(csv_file=File(f), type="account")
            a.clean()
            a.save()

        a1 = AccountStatements.objects.get()
        self.assertEqual(len(a1.payment_set.all()), 3)
        self.assertEqual(a1.date_from, datetime.date(day=25, month=1, year=2016))
        self.assertEqual(a1.date_to, datetime.date(day=31, month=1, year=2016))
        user = UserInCampaign.objects.get(pk=2978)

        p1 = Payment.objects.get(account=2150508001)
        self.assertEqual(p1.date, datetime.date(day=18, month=1, year=2016))
        self.assertEqual(p1.amount, 250)
        self.assertEqual(p1.account, '2150508001')
        self.assertEqual(p1.bank_code, '5500')
        self.assertEqual(p1.VS, '120127010')
        self.assertEqual(p1.SS, "12321")
        self.assertEqual(p1.KS, '0101')
        self.assertEqual(p1.user_identification, 'Account note')
        self.assertEqual(p1.type, 'bank-transfer')
        self.assertEqual(p1.done_by, "Done by")
        self.assertEqual(p1.account_name, "Testing user account")
        self.assertEqual(p1.bank_name, "Raiffeisenbank a.s.")
        self.assertEqual(p1.transfer_note, "Testing user note")
        self.assertEqual(p1.currency, "CZK")
        self.assertEqual(p1.recipient_message, "Message for recepient")
        self.assertEqual(p1.operation_id, "12366")
        self.assertEqual(p1.transfer_type, "Bezhotovostní příjem")
        self.assertEqual(p1.specification, "Account specification")
        self.assertEqual(p1.order_id, "1232")
        self.assertEqual(p1.user, user)

        self.assertEqual(user.payment_set.get(date=datetime.date(2016, 1, 18)), a1.payment_set.get(account=2150508001))

        unpaired_payment = a1.payment_set.get(VS=130430002)
        unpaired_payment.VS = 130430001
        unpaired_payment.save()
        user1 = UserInCampaign.objects.get(pk=2979)
        admin.pair_variable_symbols(None, None, [a1, ])
        self.assertEqual(user1.payment_set.get(), a1.payment_set.get(VS=130430001))

    def test_darujme_statement(self):
        with open("apps/aklub/test_data/test_darujme.xls", "rb") as f:
            a = AccountStatements(csv_file=File(f), type="darujme")
            a.clean()
            a.save()

        a1 = AccountStatements.objects.get()
        self.assertEqual(len(a1.payment_set.all()), 3)
        user = UserInCampaign.objects.get(pk=2978)
        self.assertEqual(user.payment_set.get(date=datetime.date(2016, 1, 20)), a1.payment_set.get(amount=200))
        unknown_user = UserInCampaign.objects.get(userprofile__user__email="unknown@email.cz")
        self.assertEqual(unknown_user.payment_set.get(date=datetime.date(2016, 1, 19)).amount, 150)


class AdminImportExportTests(TestCase):
    fixtures = ['conditions', 'users', 'communications']

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_superuser(
            username='admin', email='test_user@test_user.com', password='admin')
        self.client.force_login(self.user)

    def test_userattendance_export(self):
        address = "/admin/aklub/userincampaign/export/"
        post_data = {
            'file_format': 0,
        }
        response = self.client.post(address, post_data)
        self.assertContains(
            response,
            ',Test,User,,male,,test.user@email.cz,,Praha 4,,120127010,0,1,monthly,2015-12-16 18:22:30,'
            '"Domníváte se, že má město po zprovoznění tunelu Blanka omezit tranzit historickým centrem? Ano, hned se zprovozněním tunelu",editor,1,cs,'
        )


class FilterTests(TestCase):
    fixtures = ['conditions', 'users', 'communications']

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser(
            username='admin', email='test_user@test_user.com', password='admin')
        self.client.force_login(self.user)
        self.request = self.factory.get("")

    def test_payment_assignment_filter(self):
        f = filters.PaymentsAssignmentsFilter(self.request, {"user_assignment": "empty"}, User, None)
        q = f.queryset(self.request, Payment.objects.all())
        self.assertEquals(q.count(), 0)

    def test_user_condition_filter(self):
        f = filters.UserConditionFilter(self.request, {"user_condition": 2}, User, None)
        q = f.queryset(self.request, UserInCampaign.objects.all())
        self.assertEquals(q.count(), 2)

    def test_active_camaign_filter_no(self):
        f = filters.ActiveCampaignFilter(self.request, {"active": "no"}, User, None)
        q = f.queryset(self.request, Campaign.objects.all())
        self.assertEquals(q.count(), 0)

    def test_active_camaign_filter_yes(self):
        f = filters.ActiveCampaignFilter(self.request, {"active": "yes"}, User, None)
        q = f.queryset(self.request, Campaign.objects.all())
        self.assertEquals(q.count(), 2)

    def test_email_filter(self):
        f = filters.EmailFilter(self.request, {}, User, None)
        q = f.queryset(self.request, UserInCampaign.objects.all())
        self.assertEquals(q.count(), 2)

    def test_email_filter_duplicate(self):
        f = filters.EmailFilter(self.request, {"email": "duplicate"}, User, None)
        q = f.queryset(self.request, UserInCampaign.objects.all())
        self.assertEquals(q.count(), 0)

    def test_email_filter_blank(self):
        f = filters.EmailFilter(self.request, {"email": "blank"}, User, None)
        q = f.queryset(self.request, UserInCampaign.objects.all())
        self.assertEquals(q.count(), 0)