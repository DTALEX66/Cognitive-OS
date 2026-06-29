import unittest

from app.core.text import lexical_terms


class LexicalTermsTests(unittest.TestCase):
    def test_chinese_terms_include_bigrams(self):
        terms = lexical_terms('继续修复路由并整理项目结构')

        self.assertIn('修复', terms)
        self.assertIn('路由', terms)
        self.assertIn('项目', terms)

    def test_mixed_english_and_chinese_terms(self):
        terms = lexical_terms('Cognitive-OS 路由修复 workflow')

        self.assertIn('cognitive-os', terms)
        self.assertIn('workflow', terms)
        self.assertIn('路由', terms)
        self.assertIn('修复', terms)


if __name__ == '__main__':
    unittest.main()
