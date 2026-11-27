"""Regression checks for missing/duplicated rows in the student's QA checklist."""
import copy
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'd14_2A202603176/verify_submission.py'
spec = importlib.util.spec_from_file_location('student_submission_audit', SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class TestReviewCoverage(unittest.TestCase):
    def setUp(self):
        box = dict(label='Car', x=1., y=2., z=0., length=4., width=2., height=1.5, yaw=0.)
        self.references = {'A': {'s01f18': [box, dict(box, x=8.)]}}
        self.snapshot = {'frame_mapping': {'A': {'s01f18': {'frame_index': 0, 'first_object_id': 1}}}}
        self.rows = [dict(part='A', frame='s01f18', reference_idx=str(i), cvat_frame='0',
                          cvat_object_id=str(i), dist_m='2.2', points_in='10', ground_gap_m='0.0',
                          flags='review' if i == 1 else '', **{k: str(v) for k, v in b.items()})
                     for i, b in enumerate(self.references['A']['s01f18'], 1)]
        self.qa = [dict(row, idx=row['reference_idx']) for row in self.rows]
        self.warnings = [copy.deepcopy(self.rows[0])]

    def validate(self, rows=None, warnings=None):
        audit.validate_review_tables(self.rows if rows is None else rows, self.qa,
                                     self.warnings if warnings is None else warnings,
                                     self.references, self.snapshot)

    def test_valid_tables_cover_every_box(self):
        self.validate()

    def test_duplicate_row_cannot_hide_missing_box_at_same_row_count(self):
        with self.assertRaisesRegex(ValueError, 'duplicate box'):
            self.validate(rows=[self.rows[0], copy.deepcopy(self.rows[0])])

    def test_zero_index_cannot_alias_last_python_list_element(self):
        rows = copy.deepcopy(self.rows)
        rows[1]['reference_idx'] = '0'
        with self.assertRaisesRegex(ValueError, 'invalid one-based index'):
            self.validate(rows=rows)

    def test_missing_warning_row_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'missing boxes'):
            self.validate(warnings=[])


if __name__ == '__main__':
    unittest.main()
