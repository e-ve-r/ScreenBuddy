import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from browser_research import BrowserResearch, starting_url, rank_links


class ResearchTests(unittest.TestCase):
    def test_waits_for_manual_verification_before_continuing(self):
        with tempfile.TemporaryDirectory() as directory:
            agent = SimpleNamespace(args=SimpleNamespace(verification_timeout=10),
                                    artifact_dir=Path(directory), update_status=Mock())
            page = Mock()
            page.evaluate.side_effect = [True, True, False]
            self.assertTrue(BrowserResearch(agent).wait_for_verification(page, "news"))
            self.assertEqual(page.wait_for_timeout.call_count, 2)
            agent.update_status.assert_called_once()

    def test_skips_wait_when_there_is_no_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            agent = SimpleNamespace(args=SimpleNamespace(), artifact_dir=Path(directory))
            page = Mock()
            page.evaluate.return_value = False
            self.assertFalse(BrowserResearch(agent).wait_for_verification(page, "news"))
            page.wait_for_timeout.assert_not_called()

    def test_resolves_explicit_site_without_searching_instruction(self):
        self.assertEqual(starting_url("go to bbc and look for latest international news"),
                         "https://www.bbc.com/news")
        self.assertEqual(starting_url("research climate", "example.com/science"),
                         "https://example.com/science")

    def test_prioritizes_world_section_and_excludes_visited(self):
        links = [{"title": "World", "url": "https://www.bbc.com/news/world"},
                 {"title": "Sport", "url": "https://www.bbc.com/sport"}]
        self.assertEqual(rank_links(links, "international news", set(), "www.bbc.com")[0], links[0])
        self.assertEqual(rank_links(links, "international news", {links[0]["url"]}, "www.bbc.com"), [links[1]])

    def test_only_observed_paragraphs_and_urls_are_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            agent = SimpleNamespace(args=SimpleNamespace(), artifact_dir=Path(directory))
            research = BrowserResearch(agent)
            paragraphs = ["Observed evidence. " * 45, "Additional observed evidence. " * 20]
            with patch.object(research, "ask", return_value={
                "relevant": True, "paragraph_ids": [0, 999, -1], "made_up": "Fake finding"
            }):
                self.assertEqual(research.evidence({"title": "Article", "paragraphs": paragraphs}, "news"),
                                 [paragraphs[0]])
            with patch.object(research, "ask", return_value={"link_ids": [9, -1], "url": "https://invented.test"}):
                self.assertEqual(research.choose([{"url": "https://real.test", "title": "Real"}], "news"),
                                 [{"url": "https://real.test", "title": "Real"}])


if __name__ == "__main__":
    unittest.main()
