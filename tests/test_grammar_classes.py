"""Grammar classes shared with vocabulary-mobile (vocabulary-api#16)."""

import unittest

from app.core.grammar_class_data import GRAMMAR_CLASS_SLUGS, GRAMMAR_CLASSES
from app.integrations.openrouter_client import build_sentences_prompt


class GrammarClassDataTest(unittest.TestCase):
    def test_numerals_are_the_tenth_class(self):
        self.assertEqual(len(GRAMMAR_CLASSES), 10)
        self.assertEqual(len(set(GRAMMAR_CLASS_SLUGS)), 10)
        self.assertEqual(
            GRAMMAR_CLASSES[-1],
            {
                "slug": "numerais",
                "name": "Numerais",
                "description": "Palavras que indicam quantidade, ordem, multiplicação ou fração.",
            },
        )

    def test_the_ai_prompt_lists_every_slug(self):
        prompt = build_sentences_prompt("seven")
        for slug in GRAMMAR_CLASS_SLUGS:
            self.assertIn(slug, prompt)
        self.assertIn('"seven"', prompt)


if __name__ == "__main__":
    unittest.main()
