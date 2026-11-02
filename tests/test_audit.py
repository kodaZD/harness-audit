import unittest

from harness_audit.audit import aggregate, report_by_dimension


class AuditTests(unittest.TestCase):
    def test_aggregate_counts_skills_and_mcp(self):
        sessions = [{
            "session_id": "s1",
            "metrics": {"tool_calls": 4, "tool_errors": 1, "tokens_input": 10, "tokens_output": 2, "cost_usd": 0.1, "delegations": 0},
            "tool_counts": {"skill": 1},
            "error_signatures": {"gitnexus_impact: failure": 1},
            "skills": {"gitnexus-review": 1},
            "mcp": {"gitnexus:gitnexus_impact": 2},
            "outcome": "changed_with_validation_signal",
        }]
        result = aggregate(sessions)
        self.assertEqual(result["session_count"], 1)
        self.assertEqual(result["skills"], [("gitnexus-review", 1)])
        self.assertEqual(result["mcp"], [("gitnexus:gitnexus_impact", 2)])


    def test_dimension_report_has_rates(self):
        sessions = [{
            "session_id": "s1",
            "skills": {"docker": 1},
            "mcp": {},
            "error_signatures": {},
            "outcome": "changed_with_validation_signal",
        }]
        row = report_by_dimension(sessions, "skills")["rows"][0]
        self.assertEqual(row["name"], "docker")
        self.assertEqual(row["validation_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
