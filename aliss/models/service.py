import uuid

from django.db import models
from django.urls import reverse
from django.dispatch import receiver
from django.utils.text import slugify


class ServiceArea(models.Model):
    COUNTRY = 0
    REGION = 1
    LOCAL_AUTHORITY = 2
    HEALTH_BOARD = 3
    INTEGRATION_AUTHORITY = 4

    AREA_TYPES = (
        (COUNTRY, "Country"),
        (REGION, "Region"),
        (LOCAL_AUTHORITY, "Local Authority"),
        (HEALTH_BOARD, "Health Board"),
        (INTEGRATION_AUTHORITY, "Integration Authority (HSCP)")
    )

    name = models.CharField(max_length=100)
    alternative_name = models.CharField(max_length=100, blank=True)
    code = models.CharField(max_length=9)
    type = models.IntegerField(choices=AREA_TYPES, blank=True)

    def __str__(self):
        return self.name


class ServiceProblem(models.Model):
    UNRESOLVED = 0
    RESOLVED = 1

    STATUS_TYPES = (
        (UNRESOLVED, "Unresolved"),
        (RESOLVED, "Resolved")
    )

    INFORMATION_UNCLEAR = 0
    CONTACT_INFORMATION_INCORRECT = 10
    SERVICE_CLOSED = 20
    AREA_INCORRECT = 30

    REPORT_TYPES = (
        (INFORMATION_UNCLEAR, "Information provided is unclear"),
        (CONTACT_INFORMATION_INCORRECT, "Contact information incorrect or no response"),
        (SERVICE_CLOSED, "This service no longer exists"),
        (AREA_INCORRECT, "This service does not operate in my area")
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    service = models.ForeignKey('aliss.Service')
    user = models.ForeignKey('aliss.ALISSUser')

    type = models.IntegerField(choices=REPORT_TYPES)

    message = models.TextField(blank=True)

    status = models.IntegerField(
        choices=STATUS_TYPES,
        default=UNRESOLVED,
        blank=True
    )

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Problem with {0}".format(self.service)

    def get_absolute_url(self):
        return reverse('service_problem_detail', args=[str(self.id)])


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    organisation = models.ForeignKey('aliss.Organisation', related_name='services')
    slug = models.CharField(max_length=120, null=True, blank=True, default=None)
    name = models.CharField(max_length=100)
    description = models.TextField()
    url = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)

    categories = models.ManyToManyField('aliss.Category', related_name='services')

    locations = models.ManyToManyField(
        'aliss.Location',
        blank=True,
        related_name='services'
    )
    service_areas = models.ManyToManyField(ServiceArea, blank=True, related_name='services')

    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'aliss.ALISSUser',
        related_name='created_services',
        null=True,
        on_delete=models.SET_NULL
    )
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        'aliss.ALISSUser',
        related_name='updated_services',
        null=True,
        on_delete=models.SET_NULL
    )

    def is_edited_by(self, user):
        if user == None or user.pk == None:
            return False
        return (
            user.is_staff or \
            user.is_editor or \
            self.organisation.created_by == user or \
            self.organisation.claimed_by == user
        )

    def generate_slug(self, force=False):
        if force or self.slug == None:
            s = slugify(self.name)
            sCount = Service.objects.filter(slug__icontains=s).count()
            self.slug = s + "-" + str(sCount)
            return self.slug
        return False

    def save(self, *args, **kwargs):
        self.generate_slug()
        super(Service, self).save(*args, **kwargs)

    @property
    def is_claimed(self):
        return self.organisation.is_claimed

    def __str__(self):
        return self.name
