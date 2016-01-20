from django.test import TestCase
from aldp.models import Season, Turn, Question
from django.contrib.auth.models import User

class ModelTests(TestCase):
    fixtures=['devel']

    def test_getters(self):
        moderator = User.objects.get(username='user1')
        season = Season(number=1, title='Le retour', slug='le-retour',
                        description='Une partie pour du beurre', author=moderator)
        season.save()
        turn = Turn(number=1, author=moderator)
        turn.save()
        question = Question(text='Un pays d\'Europe', approved=True, author=moderator)
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
