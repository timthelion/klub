# Generated by Django 2.1.5 on 2019-01-28 09:54

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_grapesjs.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('aklub', '0011_auto_20180914_2106'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_account', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'verbose_name': 'Bank account',
                'verbose_name_plural': 'Bank accounts',
            },
        ),
        migrations.CreateModel(
            name='DonorPaymentChannel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('VS', models.CharField(blank=True, help_text='Variable symbol', max_length=30, null=True, verbose_name='VS')),
                ('registered_support', models.DateTimeField(blank=True, default=django.utils.timezone.now, help_text='When did this user register to support us', verbose_name='Registered support')),
                ('regular_frequency', models.CharField(blank=True, choices=[('monthly', 'Monthly'), ('quaterly', 'Quaterly'), ('biannually', 'Bianually'), ('annually', 'Anually'), (None, 'Onetime')], max_length=20, null=True, verbose_name='Frequency of regular payments')),
                ('expected_date_of_first_payment', models.DateField(blank=True, help_text='When should the first payment arrive on our account', null=True, verbose_name='Expected date of first payment')),
                ('regular_amount', models.PositiveIntegerField(blank=True, help_text='Minimum yearly payment is 1800 Kč', null=True, verbose_name='Regularly (amount)')),
                ('exceptional_membership', models.BooleanField(default=False, help_text='In special cases, people can become members of the club even if they do not pay any money. This should be justified in the note.', verbose_name='Exceptional membership')),
                ('regular_payments', models.CharField(choices=[('regular', 'Regular payments'), ('onetime', 'No regular payments'), ('promise', 'Promise of regular payments')], default='regular', help_text='Is this user registered for regular payments?', max_length=20, verbose_name='Regular payments')),
                ('old_account', models.BooleanField(default=False, help_text='User has old account', verbose_name='Old account')),
                ('other_support', models.TextField(blank=True, help_text='If the user supports us in other ways, please specify here.', max_length=500, verbose_name='Other support')),
                ('bank_account', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='bankaccounts', to='aklub.BankAccount')),
            ],
            options={
                'verbose_name': 'Donor payment channel',
                'verbose_name_plural': 'Donor payment channels',
            },
        ),
        migrations.CreateModel(
            name='Interaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(choices=[('email', 'Email'), ('phonecall', 'Phonecall'), ('mail', 'Mail'), ('personal', 'Personal'), ('internal', 'Internal')], max_length=30, verbose_name='Method')),
                ('type', models.CharField(choices=[('mass', 'Mass'), ('auto', 'Automatic'), ('individual', 'Individual')], default='individual', max_length=30, verbose_name='Type of communication')),
                ('date', models.DateTimeField(verbose_name='Date')),
                ('subject', models.CharField(help_text='The topic of this communication', max_length=130, verbose_name='Subject')),
                ('summary', models.TextField(help_text='Text or summary of this communication', max_length=50000, verbose_name='Text')),
                ('attachment', models.FileField(blank=True, null=True, upload_to='communication-attachments', verbose_name='Attachment')),
                ('note', models.TextField(blank=True, help_text='Internal notes about this communication', max_length=3000, verbose_name='Notes')),
                ('send', models.BooleanField(default=False, help_text='Request sending or resolving this communication. For emails, this means that the email will be immediatelly sent to the user. In other types of communications, someone must handle this manually.', verbose_name='Send / Handle')),
                ('dispatched', models.BooleanField(default=False, help_text='Was this message already sent, communicated and/or resolved?', verbose_name='Dispatched / Done')),
            ],
            options={
                'verbose_name': 'Interaction',
                'verbose_name_plural': 'Interactions',
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='Telephone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telephone', models.CharField(blank=True, max_length=100, validators=[django.core.validators.RegexValidator('^\\+?(42(0|1){1})?\\s?\\d{3}\\s?\\d{3}\\s?\\d{3}$', 'Telephone must consist of numbers, spaces and + sign or maximum number count is higher.')], verbose_name='Telephone number')),
                ('is_primary', models.BooleanField(blank=True, default=False, verbose_name='Primary phone')),
            ],
            options={
                'verbose_name': 'Telephone',
                'verbose_name_plural': 'Telephones',
            },
        ),
        migrations.RenameModel(
            old_name='Campaign',
            new_name='Event',
        ),
        migrations.RemoveField(
            model_name='communication',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='communication',
            name='handled_by',
        ),
        migrations.RemoveField(
            model_name='communication',
            name='result',
        ),
        migrations.RemoveField(
            model_name='communication',
            name='user',
        ),
        migrations.AlterModelOptions(
            name='event',
            options={'verbose_name': 'Event', 'verbose_name_plural': 'Events'},
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='telephone',
        ),
        migrations.AlterField(
            model_name='masscommunication',
            name='send_to_users',
            field=models.ManyToManyField(blank=True, help_text='All users who should receive the communication', limit_choices_to={'userprofile__is_active': 'True', 'userprofile__send_mailing_lists': 'True', 'wished_information': 'True'}, to='aklub.UserInCampaign', verbose_name='send to users'),
        ),
        migrations.AlterField(
            model_name='masscommunication',
            name='template',
            field=django_grapesjs.models.fields.GrapesJsHtmlField(),
        ),
        migrations.AlterField(
            model_name='terminalcondition',
            name='variable',
            field=models.CharField(blank=True, choices=[('User.date_joined', 'User datum registrace: DateTimeField '), ('User.email', 'User e-mailová adresa: CharField '), ('User.first_name', 'User křestní jméno: CharField '), ('User.id', 'User ID: AutoField '), ('User.is_active', 'User aktivní: BooleanField '), ('User.is_staff', 'User administrační přístup: BooleanField '), ('User.is_superuser', 'User superuživatel: BooleanField '), ('User.last_login', 'User poslední přihlášení: DateTimeField '), ('User.last_name', 'User příjmení: CharField '), ('User.password', 'User heslo: CharField '), ('User.username', 'User uživatelské jméno: CharField '), ('User.last_payment.BIC', 'User.last_payment BIC: CharField '), ('User.last_payment.KS', 'User.last_payment CS: CharField '), ('User.last_payment.SS', 'User.last_payment SS: CharField '), ('User.last_payment.VS', 'User.last_payment VS: CharField '), ('User.last_payment.account', 'User.last_payment Account: CharField '), ('User.last_payment.account_name', 'User.last_payment Account name: CharField '), ('User.last_payment.account_statement', 'User.last_payment account statement: ForeignKey '), ('User.last_payment.amount', 'User.last_payment Amount: PositiveIntegerField '), ('User.last_payment.bank_code', 'User.last_payment Bank code: CharField '), ('User.last_payment.bank_name', 'User.last_payment Bank name: CharField '), ('User.last_payment.created', 'User.last_payment Date of creation: DateTimeField '), ('User.last_payment.currency', 'User.last_payment Currency: CharField '), ('User.last_payment.date', 'User.last_payment Date of payment: DateField '), ('User.last_payment.done_by', 'User.last_payment Done by: CharField '), ('User.last_payment.id', 'User.last_payment ID: AutoField '), ('User.last_payment.operation_id', 'User.last_payment Operation ID: CharField '), ('User.last_payment.order_id', 'User.last_payment Order ID: CharField '), ('User.last_payment.recipient_message', 'User.last_payment Recipient message: CharField '), ('User.last_payment.specification', 'User.last_payment Specification: CharField '), ('User.last_payment.transfer_note', 'User.last_payment Transfer note: CharField '), ('User.last_payment.transfer_type', 'User.last_payment Transfer type: CharField '), ('User.last_payment.type', "User.last_payment Typ: CharField ('bank-transfer', 'cash', 'expected', 'darujme')"), ('User.last_payment.updated', 'User.last_payment Date of last change: DateTimeField '), ('User.last_payment.user', 'User.last_payment user: ForeignKey '), ('User.last_payment.user_donor_payment_channel', 'User.last_payment user donor payment channel: ForeignKey '), ('User.last_payment.user_identification', 'User.last_payment Sender identification: CharField '), ('User.source.direct_dialogue', 'User.source Is from Direct Dialogue: BooleanField '), ('User.source.id', 'User.source ID: AutoField '), ('User.source.name', 'User.source Název: CharField '), ('User.source.slug', 'User.source Slug: SlugField '), ('UserInCampaign.activity_points', 'UserInCampaign Activity points: IntegerField '), ('UserInCampaign.additional_information', 'UserInCampaign Additional information: TextField '), ('UserInCampaign.campaign', 'UserInCampaign campaign: ForeignKey '), ('UserInCampaign.created', 'UserInCampaign Date of creation: DateTimeField '), ('UserInCampaign.email_confirmed', 'UserInCampaign Is confirmed via e-mail: BooleanField '), ('UserInCampaign.end_of_regular_payments', 'UserInCampaign End of regular payments (for payments by card): DateField '), ('UserInCampaign.exceptional_membership', 'UserInCampaign Exceptional membership: BooleanField '), ('UserInCampaign.expected_date_of_first_payment', 'UserInCampaign Expected date of first payment: DateField '), ('UserInCampaign.expected_regular_payment_date', 'UserInCampaign expected regular payment date: DateField '), ('UserInCampaign.extra_money', 'UserInCampaign extra money: IntegerField '), ('UserInCampaign.field_of_work', 'UserInCampaign Field of work: CharField '), ('UserInCampaign.gdpr_consent', 'UserInCampaign GDPR consent: BooleanField '), ('UserInCampaign.id', 'UserInCampaign ID: AutoField '), ('UserInCampaign.knows_us_from', 'UserInCampaign Where does he/she know us from?: CharField '), ('UserInCampaign.last_payment', 'UserInCampaign last payment: DenormDBField '), ('UserInCampaign.next_communication_date', 'UserInCampaign Date of next communication: DateField '), ('UserInCampaign.next_communication_method', "UserInCampaign Method of next communication: CharField ('email', 'phonecall', 'mail', 'personal', 'internal')"), ('UserInCampaign.no_upgrade', 'UserInCampaign no upgrade: NullBooleanField '), ('UserInCampaign.note', 'UserInCampaign Note for making a boring form more lively: TextField '), ('UserInCampaign.number_of_payments', 'UserInCampaign number of payments: IntegerField '), ('UserInCampaign.old_account', 'UserInCampaign Old account: BooleanField '), ('UserInCampaign.other_support', 'UserInCampaign Other support: TextField '), ('UserInCampaign.payment_total', 'UserInCampaign payment total: FloatField '), ('UserInCampaign.public', 'UserInCampaign Publish my name in the list of supporters/petitents of this campaign: BooleanField '), ('UserInCampaign.recruiter', 'UserInCampaign recruiter: ForeignKey '), ('UserInCampaign.registered_support', 'UserInCampaign Registered support: DateTimeField '), ('UserInCampaign.regular_amount', 'UserInCampaign Regularly (amount): PositiveIntegerField '), ('UserInCampaign.regular_frequency', "UserInCampaign Frequency of regular payments: CharField ('monthly', 'quaterly', 'biannually', 'annually', None)"), ('UserInCampaign.regular_payments', "UserInCampaign Regular payments: CharField ('regular', 'onetime', 'promise')"), ('UserInCampaign.source', 'UserInCampaign Source: ForeignKey '), ('UserInCampaign.updated', 'UserInCampaign Date of last change: DateTimeField '), ('UserInCampaign.userprofile', 'UserInCampaign userprofile: ForeignKey '), ('UserInCampaign.variable_symbol', 'UserInCampaign Variable symbol: CharField '), ('UserInCampaign.verified', 'UserInCampaign Verified: BooleanField '), ('UserInCampaign.verified_by', 'UserInCampaign Verified by: ForeignKey '), ('UserInCampaign.why_supports', 'UserInCampaign Why does he/she support us?: TextField '), ('UserInCampaign.wished_information', 'UserInCampaign Send regular news via email: BooleanField '), ('UserInCampaign.wished_tax_confirmation', 'UserInCampaign Send tax confirmation: BooleanField '), ('UserInCampaign.wished_welcome_letter', 'UserInCampaign Send welcome letter: BooleanField '), ('UserProfile.addressment', 'UserProfile Addressment in letter: CharField '), ('UserProfile.addressment_on_envelope', 'UserProfile Addressment on envelope: CharField '), ('UserProfile.age_group', 'UserProfile Birth year: PositiveIntegerField (2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007, 2006, 2005, 2004, 2003, 2002, 2001, 2000, 1999, 1998, 1997, 1996, 1995, 1994, 1993, 1992, 1991, 1990, 1989, 1988, 1987, 1986, 1985, 1984, 1983, 1982, 1981, 1980, 1979, 1978, 1977, 1976, 1975, 1974, 1973, 1972, 1971, 1970, 1969, 1968, 1967, 1966, 1965, 1964, 1963, 1962, 1961, 1960, 1959, 1958, 1957, 1956, 1955, 1954, 1953, 1952, 1951, 1950, 1949, 1948, 1947, 1946, 1945, 1944, 1943, 1942, 1941, 1940, 1939, 1938, 1937, 1936, 1935, 1934, 1933, 1932, 1931, 1930, 1929, 1928, 1927, 1926, 1925, 1924, 1923, 1922, 1921, 1920)'), ('UserProfile.city', 'UserProfile City/City part: CharField '), ('UserProfile.club_card_available', 'UserProfile Club card available: BooleanField '), ('UserProfile.club_card_dispatched', 'UserProfile Club card dispatched?: BooleanField '), ('UserProfile.country', 'UserProfile Country: CharField '), ('UserProfile.created', 'UserProfile Date of creation: DateTimeField '), ('UserProfile.date_joined', 'UserProfile datum registrace: DateTimeField '), ('UserProfile.different_correspondence_address', 'UserProfile Different correspondence address: BooleanField '), ('UserProfile.email', 'UserProfile e-mailová adresa: CharField '), ('UserProfile.first_name', 'UserProfile křestní jméno: CharField '), ('UserProfile.id', 'UserProfile ID: AutoField '), ('UserProfile.is_active', 'UserProfile aktivní: BooleanField '), ('UserProfile.is_staff', 'UserProfile administrační přístup: BooleanField '), ('UserProfile.is_superuser', 'UserProfile superuživatel: BooleanField '), ('UserProfile.language', "UserProfile Language: CharField ('cs', 'en')"), ('UserProfile.last_login', 'UserProfile poslední přihlášení: DateTimeField '), ('UserProfile.last_name', 'UserProfile příjmení: CharField '), ('UserProfile.note', 'UserProfile Note for making a boring form more lively: TextField '), ('UserProfile.other_benefits', 'UserProfile Other benefits: TextField '), ('UserProfile.other_support', 'UserProfile Other support: TextField '), ('UserProfile.password', 'UserProfile heslo: CharField '), ('UserProfile.profile_picture', 'UserProfile Profile picture: FileField '), ('UserProfile.profile_text', 'UserProfile What is your reason?: TextField '), ('UserProfile.public', 'UserProfile Publish my name in the list of supporters: BooleanField '), ('UserProfile.send_mailing_lists', 'UserProfile Sending of mailing lists allowed: BooleanField '), ('UserProfile.sex', "UserProfile Gender: CharField ('male', 'female', 'unknown')"), ('UserProfile.street', 'UserProfile Street and number: CharField '), ('UserProfile.title_after', 'UserProfile Title after name: CharField '), ('UserProfile.title_before', 'UserProfile Title before name: CharField '), ('UserProfile.updated', 'UserProfile Date of last change: DateTimeField '), ('UserProfile.username', 'UserProfile uživatelské jméno: CharField '), ('UserProfile.zip_code', 'UserProfile ZIP Code: TextField '), ('action', "Operace: CharField ('daily', 'new-user', 'new-payment')")], help_text='Value or variable on left-hand side', max_length=50, null=True, verbose_name='Variable'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='age_group',
            field=models.PositiveIntegerField(blank=True, choices=[(2019, 2019), (2018, 2018), (2017, 2017), (2016, 2016), (2015, 2015), (2014, 2014), (2013, 2013), (2012, 2012), (2011, 2011), (2010, 2010), (2009, 2009), (2008, 2008), (2007, 2007), (2006, 2006), (2005, 2005), (2004, 2004), (2003, 2003), (2002, 2002), (2001, 2001), (2000, 2000), (1999, 1999), (1998, 1998), (1997, 1997), (1996, 1996), (1995, 1995), (1994, 1994), (1993, 1993), (1992, 1992), (1991, 1991), (1990, 1990), (1989, 1989), (1988, 1988), (1987, 1987), (1986, 1986), (1985, 1985), (1984, 1984), (1983, 1983), (1982, 1982), (1981, 1981), (1980, 1980), (1979, 1979), (1978, 1978), (1977, 1977), (1976, 1976), (1975, 1975), (1974, 1974), (1973, 1973), (1972, 1972), (1971, 1971), (1970, 1970), (1969, 1969), (1968, 1968), (1967, 1967), (1966, 1966), (1965, 1965), (1964, 1964), (1963, 1963), (1962, 1962), (1961, 1961), (1960, 1960), (1959, 1959), (1958, 1958), (1957, 1957), (1956, 1956), (1955, 1955), (1954, 1954), (1953, 1953), (1952, 1952), (1951, 1951), (1950, 1950), (1949, 1949), (1948, 1948), (1947, 1947), (1946, 1946), (1945, 1945), (1944, 1944), (1943, 1943), (1942, 1942), (1941, 1941), (1940, 1940), (1939, 1939), (1938, 1938), (1937, 1937), (1936, 1936), (1935, 1935), (1934, 1934), (1933, 1933), (1932, 1932), (1931, 1931), (1930, 1930), (1929, 1929), (1928, 1928), (1927, 1927), (1926, 1926), (1925, 1925), (1924, 1924), (1923, 1923), (1922, 1922), (1921, 1921), (1920, 1920)], null=True, verbose_name='Birth year'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='sex',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('unknown', 'Unknown')], default='unknown', max_length=50, verbose_name='Gender'),
        ),

        migrations.DeleteModel(
            name='Communication',
        ),
        migrations.AddField(
            model_name='telephone',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='interaction',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_by_communication', to=settings.AUTH_USER_MODEL, verbose_name='Created by'),
        ),
        migrations.AddField(
            model_name='interaction',
            name='event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events', to='aklub.Event', verbose_name='Event'),
        ),
        migrations.AddField(
            model_name='interaction',
            name='handled_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='handled_by_communication', to=settings.AUTH_USER_MODEL, verbose_name='Last handled by'),
        ),
        migrations.AddField(
            model_name='interaction',
            name='result',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='aklub.Result', verbose_name='Result of communication'),
        ),
        migrations.AddField(
            model_name='interaction',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='communications', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AddField(
            model_name='donorpaymentchannel',
            name='event',
            field=models.ManyToManyField(blank=True, null=True, related_name='donorevents', to='aklub.Event', verbose_name='Event'),
        ),
        migrations.AddField(
            model_name='donorpaymentchannel',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='userchannels', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AddField(
            model_name='payment',
            name='user_donor_payment_channel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='paymentchannels', to='aklub.DonorPaymentChannel'),
        ),
        migrations.AlterUniqueTogether(
            name='donorpaymentchannel',
            unique_together={('VS', 'bank_account')},
        ),
    ]
