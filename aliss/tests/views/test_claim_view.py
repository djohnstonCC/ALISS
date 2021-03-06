from django.test import TestCase, Client
from django.urls import reverse
from aliss.models import Organisation, ALISSUser, Service, Location, Claim

class ClaimViewTestCase(TestCase):
    def setUp(self):
        self.user     = ALISSUser.objects.create_user("main@user.org", "passwurd")
        self.punter   = ALISSUser.objects.create_user("random@random.org", "passwurd")
        self.staff   = ALISSUser.objects.create_user("staff@aliss.org", "passwurd",  is_staff=True)
        self.editor   = ALISSUser.objects.create_user("updater@aliss.org", "passwurd",  is_editor=True)
        self.client.login(username='main@user.org', password='passwurd')
        self.organisation = Organisation.objects.create(
          name="TestOrg",
          description="A test description",
          created_by=self.punter
        )

    def test_claim_list(self):
        response = self.client.get(reverse('claim_list', kwargs={}))
        self.assertEqual(response.status_code, 302)
        self.client.login(username='staff@aliss.org', password='passwurd')
        response = self.client.get(reverse('claim_list', kwargs={}))
        self.assertEqual(response.status_code, 200)

    def test_claim_create(self):
        response = self.client.get(reverse('claim_create', kwargs={'pk': self.organisation.pk}))
        self.assertEqual(response.status_code, 200)

    def test_logout_claim_create(self):
        self.client.logout()
        response = self.client.get(reverse('claim_create', kwargs={'pk': self.organisation.pk}))
        self.assertEqual(response.status_code, 302)

'''
    def test_claim_invalid_creation(self):
        response = self.client.post(reverse('organisation_create'), { 'name': '' })
        self.assertEqual(Organisation.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

    def test_claim_valid_creation(self):
        response = self.client.post(reverse('organisation_create'), 
            { 'name': 'an organisation', 'description': 'a full description' })
        o = Organisation.objects.latest('created_on')

        self.assertEqual(o.name, 'an organisation')
        self.assertEqual(o.published, False)
        self.assertEqual(response.status_code, 302)

    def test_claim_valid_creation_with_editor(self):
        self.client.login(username='updater@aliss.org', password='passwurd')
        response = self.client.post(reverse('organisation_create'), 
            { 'name': 'an organisation', 'description': 'a full description' })
        o = Organisation.objects.latest('created_on')

        self.assertEqual(o.name, 'an organisation')
        self.assertEqual(o.published, True)
        self.assertEqual(response.status_code, 302)


    def test_unpublished_organisation_detail(self):
        self.organisation.published = False
        self.organisation.save()

        response_1 = self.client.get(reverse('organisation_detail', kwargs={'pk': self.organisation.pk}))
        self.client.login(username='random@random.org', password='passwurd')
        response_2 = self.client.get(reverse('organisation_detail', kwargs={'pk': self.organisation.pk}))
        self.client.login(username='claimant@random.org', password='passwurd')
        response_3 = self.client.get(reverse('organisation_detail', kwargs={'pk': self.organisation.pk}))

        self.assertEqual(response_1.status_code, 200)
        self.assertEqual(response_2.status_code, 403)
        self.assertEqual(response_3.status_code, 200)

    def test_claim_delete(self):
        response = self.client.delete((reverse('organisation_delete', kwargs={'pk': self.organisation.pk})))
        self.assertRedirects(response, (reverse('account_my_organisations')))

    def test_claim_unpublished(self):
        response = self.client.get(reverse('organisation_unpublished'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username='staff@aliss.org', password='passwurd')
        response = self.client.get(reverse('organisation_unpublished'))
        self.assertEqual(response.status_code, 200)

    def test_claim_publish(self):
        self.organisation.published = False
        self.organisation.save()
        self.client.login(username='staff@aliss.org', password='passwurd')
        response = self.client.post(reverse('organisation_publish', kwargs={'pk': self.organisation.pk}))
        self.organisation.refresh_from_db()
        self.assertTrue(self.organisation.published)
        self.assertRedirects(response, (reverse('organisation_detail', kwargs={'pk': self.organisation.pk})))
'''