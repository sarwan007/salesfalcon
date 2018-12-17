from rest_framework import serializers
from .models import ( Company,
                      UserProfile,
                      Customer,
                      DeliveredMessage,
                      MeetingNote,
                      MeetingReminder)
from django.contrib.auth.models import User


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('name', 'industry', 'revenue', 'email', 'phone_no', 'stock_market',
                  'address', 'city', 'state', 'country', 'website', 'linkedin')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        extra_kwargs = {'password': {'write_only': True}}
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'password')

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = UserProfile
        fields = ('owner', 'mobile', 'profession', 'experience', 'address', 'city',
                  'dob', 'bio', 'state', 'country', 'company', 'facebook', 'linkedin')

    def create(self, validated_data):
        company_details = validated_data.pop('company')
        if Company.objects.filter(name=company_details['name'], city=company_details['city']).exists():
            company = Company.objects.get(name=company_details['name'], city=company_details['city'])
            user = UserProfile.objects.create(company=company, **validated_data)
            return user
        company = Company.objects.create(**company_details)
        user = UserProfile.objects.create(company=company, **validated_data)
        return user

    def update(self, instance, validated_data):
        company = instance.company
        company_details = validated_data.pop('company')
        instance.profession = validated_data.get('profession', instance.profession)
        instance.experience = validated_data.get('experience', instance.experience)
        instance.dob = validated_data.get('dob', instance.dob)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.address = validated_data.get('address', instance.address)
        instance.city = validated_data.get('city', instance.city)
        instance.country = validated_data.get('country', instance.country)
        instance.facebook = validated_data.get('facebook', instance.facebook)
        instance.linkedin = validated_data.get('linkedin', instance.linkedin)
        if Company.objects.filter(name=company_details['name'], city=company_details['city']).exists():
            company.revenue = company_details.get('revenue', company.revenue)
            company.linkedin = company_details.get('linkedin', company.linkedin)
            company.stock_market = company_details.get('stock_market', company.stock_market)
            company.email = company_details.get('email', company.email)
            company.phone_no = company_details.get('phone_no', company.phone_no)
            company.website = company_details.get('website', company.website)
            instance.save()
            company.save()
            return instance
        else:
            company_instance = Company.objects.create(**company_details)
            instance.company = company_instance
            instance.save()
            return instance


class UserDetailsSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    owner = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ('owner', 'mobile', 'profession', 'experience', 'address', 'city',
                  'state', 'country', 'company')


class CustomerSerializer(serializers.ModelSerializer):
    owner = UserSerializer()

    class Meta:
        model = Customer
        fields = ('owner', 'name', 'address', 'city',
                  'state', 'country', 'phone_no', 'email',
                  'linkedin', 'facebook', 'scoring', 'website')


class PotentialCustomerSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Customer
        fields = ('id', 'owner', 'name', 'address', 'city',
                  'state', 'country', 'phone_no', 'email',
                  'linkedin', 'facebook', 'scoring', 'website')


class PutDeliveredMessageSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = DeliveredMessage
        fields = ('owner', 'message_type', 'receiver', 'subject', 'message')


class FetchDeliveredMessageSerializer(serializers.ModelSerializer):
    owner = UserSerializer()

    class Meta:
        model = DeliveredMessage
        fields = ('owner', 'message_type', 'receiver', 'subject', 'message')


class SaveMeetingNotesSerializer(serializers.ModelSerializer):
    customer = serializers.ReadOnlyField(source='customer.id')

    class Meta:
        model = MeetingNote
        fields = ('customer', 'flag', 'notes')

    def update(self, instance, validated_data):
        instance.flag = validated_data.get('flag', instance.flag)
        instance.notes = validated_data.get('notes', instance.notes)
        return instance


class FetchMeetingNotesSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()

    class Meta:
        model = MeetingNote
        fields = ('id', 'customer', 'flag', 'notes')


class ReminderNotesSerializer(serializers.ModelSerializer):
    customer = serializers.ReadOnlyField(source='customer.id')
    note = serializers.ReadOnlyField(source='note.id')

    def update(self, instance, validated_data):
        instance.remind_at = validated_data.get('remind_at', instance.remind_at)
        instance.note = validated_data.get('note', instance.note)
        instance.customer = validated_data.get('customer', instance.customer)
        return instance

    class Meta:
        model = MeetingReminder
        fields = ('customer', 'note', 'remind_at')


class FetchMeetingReminderSerializer(serializers.ModelSerializer):
    note = FetchMeetingNotesSerializer()

    class Meta:
        model = MeetingReminder
        fields = ('id', 'note', 'remind_at')
