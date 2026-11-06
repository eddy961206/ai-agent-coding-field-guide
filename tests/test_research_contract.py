"""Keep historical evidence while validating new intake against current sources."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build import validate_batch
from translation_baseline import reject_untranslated_copy

class ResearchContractTests(unittest.TestCase):
    def test_archived_source_move_preserves_history_but_new_intake_is_strict(self):
        catalog={'guide':{'url':'https://example.com/new-guide'}}
        batch={'schema_version':1,'topic':'Example','as_of':'2026-11-06','timezone':'Asia/Seoul','scope':'An original article','publishing_status':'reviewed_for_publication','counterevidence':[],'access_gaps':[],'next_questions':[],'findings':[{'source_id':'guide','original_url':'https://example.com/old-guide','author':'Author','published_on':'2026-11-01','date_basis':'Original page','checked_on':'2026-11-06','source_kind':'Web','evidence_kind':'opinion','author_claim':'A claim','editorial_takeaway':'A possible use','limitations':['Not reproduced'],'related_source_ids':[],'change_type':'addition'}]}
        validate_batch(batch,catalog,historical=True)
        with self.assertRaisesRegex(ValueError,'URL conflicts'):
            validate_batch(batch,catalog)

    def test_known_source_alias_accepts_a_moved_link(self):
        from source_identity import source_keys,source_identity
        source={'url':'https://example.com/new','aliases':['https://example.com/old']}
        self.assertIn(source_identity('https://example.com/old?utm_source=x'),source_keys(source))

    def test_english_data_cannot_be_an_unchanged_korean_copy(self):
        source={'id':'method','action':'실제 동작을 확인해.'}
        with self.assertRaisesRegex(ValueError,'Untranslated English field'):
            reject_untranslated_copy(source,dict(source),('action',))
        reject_untranslated_copy(source,{'id':'method','action':'Check the actual behavior.'},('action',))

if __name__=='__main__':
    unittest.main()
