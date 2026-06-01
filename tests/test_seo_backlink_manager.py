import unittest

from seo_backlink_manager import evaluate_source, generate_report


class BacklinkManagerTests(unittest.TestCase):
    def test_relevant_resource_page_scores_high(self):
        result = evaluate_source(
            "https://example.org/content-marketing/resources",
            ["content marketing", "seo strategy"],
            "marketing software",
        )

        self.assertEqual(result.type, "Resource Page")
        self.assertEqual(result.relevance, "High")
        self.assertGreaterEqual(result.score, 75)
        self.assertEqual(result.quality, "High Quality")

    def test_toxic_source_is_flagged_and_penalized(self):
        result = evaluate_source(
            "https://free-backlinks-casino-pbn-12345.example/spam",
            ["accounting software"],
            "small business accounting",
        )

        self.assertEqual(result.quality, "Low Quality")
        self.assertTrue(result.toxic_reasons)
        self.assertLess(result.score, 50)

    def test_report_contains_dashboard_ready_sections(self):
        report = generate_report(
            website_url="https://acme.example",
            keywords=["accounting software", "invoice automation"],
            niche="small business accounting software",
            competitors=["https://competitor.example"],
            sites_list=[
                "https://accounting.example.org/resources",
                "https://smallbusinessdirectory.example/listing",
                "https://casino-pbn-free-backlinks.example",
            ],
        )

        data = report.to_dict()
        self.assertIn("source_evaluations", data)
        self.assertIn("anchor_text_suggestions", data)
        self.assertIn("backlink_building_plan", data)
        self.assertIn("content_ideas", data)
        self.assertIn("# Website Analysis", report.to_markdown())
        self.assertIn("casino-pbn", report.risk_analysis["toxic_sources"][0])


if __name__ == "__main__":
    unittest.main()
