"""Standard grammar forms, mirroring vocabulary-mobile (vocabulary-api#15)."""

import unittest

from app.core.grammar_class_data import GRAMMAR_CLASS_SLUGS
from app.core.grammar_forms import GRAMMAR_FORMS, normalize_forms


class GrammarFormsTest(unittest.TestCase):
    def test_every_class_has_a_form(self):
        self.assertEqual(sorted(GRAMMAR_FORMS), sorted(GRAMMAR_CLASS_SLUGS))

    def test_field_names_match_mobile(self):
        keys = lambda slug: [field.key for field in GRAMMAR_FORMS[slug]]
        self.assertEqual(keys("verbos"), ["third_person", "past", "past_participle", "ing", "regularity"])
        self.assertEqual(keys("substantivos"), ["plural", "countability", "gender", "derivations"])
        self.assertEqual(keys("adverbios"), ["comparative", "superlative", "source", "usage", "example"])
        self.assertEqual(keys("numerais"), ["digits", "ordinal", "multiplicative", "fractional"])
        self.assertEqual(keys("artigos"), ["usage", "example"])

    def test_trims_and_drops_empty_fields(self):
        forms, problem = normalize_forms(
            "verbos",
            {
                "past": {"english": " drank ", "portuguese": "bebeu", "spanish": "  "},
                "ing": {"english": "", "portuguese": None},
                "regularity": {"english": "irregular", "portuguese": "ignored"},
            },
        )
        self.assertIsNone(problem)
        self.assertEqual(
            forms,
            {
                "past": {"english": "drank", "portuguese": "bebeu", "spanish": None},
                "regularity": {"english": "irregular", "portuguese": None, "spanish": None},
            },
        )

    def test_rejects_bad_forms(self):
        cases = [
            ("verbos", {"plural": {"english": "x"}}, "plural"),
            ("verbos", {"past": {"portuguese": "bebeu"}}, "past"),
            ("substantivos", {"countability": {"english": "many"}}, "countability"),
            ("unknown", {"past": {"english": "x"}}, "past"),
        ]
        for slug, forms, field in cases:
            _, problem = normalize_forms(slug, forms)
            self.assertIsNotNone(problem, (slug, forms))
            self.assertIn(field, problem)


if __name__ == "__main__":
    unittest.main()
