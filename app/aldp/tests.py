from django.test import TestCase
from django.core.urlresolvers import reverse
from aldp.models import Season, Turn, Question
from django.contrib.auth.models import User

class ModelTests(TestCase):
    fixtures = ['devel']

    def test_getters(self):
        moderator = User.objects.get(username='user1')
        season = Season(number=1, title='Le retour', slug='le-retour',
                        description='Une partie pour du beurre', author=moderator)
        season.save()
        turn = Turn(author=moderator)
        turn.save()
        question = Question(text='Un pays d\'Europe', author=moderator)
        question.save()
        self.assertIsNone(question.season)
        self.assertEqual([], list(season.turn_set.all()))
        self.assertEqual([], list(turn.question_set.all()))
        question.turn = turn
        question.save()
        self.assertEqual([question], list(turn.question_set.all()))
        self.assertIsNone(question.season)
        turn.season = season
        turn.save()
        self.assertEqual([turn], list(season.turn_set.all()))
        self.assertEqual(season, question.season)

class SignalTests(TestCase):
    fixtures = ['devel']

    def test_season_start_date(self):
        moderator = User.objects.get(username='user1')
        '''Test that the season start_date is updated when a turn starts.'''
        season = Season(number=1, title='Le retour', slug='le-retour',
                        description='Une partie pour du beurre', author=moderator)
        season.save()
        turn = Turn(author=moderator)
        turn.save()
        season.attach(turn)
        self.assertIsNone(turn.start_date)
        self.assertIsNone(season.start_date)
        turn.start()
        self.assertIsNotNone(turn.start_date)
        self.assertIsNotNone(season.start_date)
        self.assertEqual(season.start_date, turn.start_date)
        self.assertIsNone(turn.end_date)

    def test_season_start_date_not_updated(self):
        moderator = User.objects.get(username='user1')
        '''Test that the season start_date is updated when a turn starts.'''
        season = Season(number=1, title='Le retour', slug='le-retour',
                        description='Une partie pour du beurre', author=moderator)
        season.save()
        turn = Turn(author=moderator)
        turn.save()
        season.attach(turn)
        season.start()
        season.save()
        self.assertIsNone(turn.start_date)
        self.assertIsNotNone(season.start_date)
        turn.start()
        self.assertIsNotNone(turn.start_date)
        self.assertIsNotNone(season.start_date)
        self.assertNotEqual(season.start_date, turn.start_date)
        self.assertIsNone(turn.end_date)

    def test_detached_turn_has_no_dates(self):
        moderator = User.objects.get(username='user1')
        '''Test that the season start_date is updated when a turn starts.'''
        season = Season(number=1, title='Le retour', slug='le-retour',
                        description='Une partie pour du beurre', author=moderator)
        season.save()
        turn = Turn(author=moderator)
        turn.save()
        season.attach(turn)
        self.assertIsNone(turn.start_date)
        self.assertIsNone(turn.end_date)
        turn.start()
        self.assertIsNotNone(turn.start_date)
        self.assertIsNone(turn.end_date)
        turn.stop()
        self.assertIsNotNone(turn.start_date)
        self.assertIsNotNone(turn.end_date)
        season.detach(turn)
        self.assertIsNone(turn.start_date)
        self.assertIsNone(turn.end_date)


class FormTests(TestCase):
    fixtures = ['devel']

    def test_season_permissions(self):
        response = self.client.get(reverse('season_create'))
        self.assertEqual(response.status_code, 302)
        nb_seasons = Season.objects.count()
        response = self.client.post(reverse('season_create'), {'number': '1',
                                                              'title': 'La première',
                                                              'description': '''La première mais pas
                                                              la dernière!'''})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Season.objects.count(), nb_seasons)

    def test_season_permissions_regular_user(self):
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('season_create'))
        self.assertEqual(response.status_code, 302)
        nb_seasons = Season.objects.count()
        response = self.client.post(reverse('season_create'), {'number': '1',
                                                              'title': 'La première',
                                                              'description': '''La première mais pas
                                                              la dernière!'''})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Season.objects.count(), nb_seasons)

    def test_season_permissions_admin_user(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('season_create'))
        self.assertEqual(response.status_code, 200)
        nb_seasons = Season.objects.count()
        response = self.client.post(reverse('season_create'), {'number': '1',
                                                              'title': 'La première',
                                                              'description': '''La première mais pas
                                                              la dernière!'''})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Season.objects.count(), nb_seasons+1)

