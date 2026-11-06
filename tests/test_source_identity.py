"""Source identity behavior at the daily research intake boundary."""
import unittest
from scripts.source_identity import source_identity

class SourceIdentityTests(unittest.TestCase):
    def test_x_alias_and_tracking_preserve_post_identity(self):
        self.assertEqual(source_identity('https://twitter.com/oldname/status/123?s=20'),source_identity('https://x.com/newname/status/123'))

    def test_distinct_x_posts_stay_distinct(self):
        self.assertNotEqual(source_identity('https://x.com/a/status/123'),source_identity('https://x.com/a/status/124'))

    def test_reddit_comment_variants_match(self):
        self.assertEqual(source_identity('https://old.reddit.com/r/codex/comments/abc/title/comment/def/?context=3'),source_identity('https://www.reddit.com/r/codex/comments/abc/comment/def/'))

    def test_reddit_comments_do_not_collapse_into_parent(self):
        parent=source_identity('https://reddit.com/r/codex/comments/abc/title/')
        comment=source_identity('https://reddit.com/r/codex/comments/abc/title/def/')
        other=source_identity('https://reddit.com/r/codex/comments/abc/title/ghi/')
        self.assertEqual(len({parent,comment,other}),3)

    def test_reddit_short_post_link_matches(self):
        self.assertEqual(source_identity('https://redd.it/abc'),source_identity('https://reddit.com/r/codex/comments/abc/title/'))

    def test_reddit_query_comments_are_distinct_and_match_paths(self):
        one=source_identity('https://reddit.com/r/codex/comments/abc/title/?comment=first1')
        two=source_identity('https://reddit.com/r/codex/comments/abc/title/?comment=second2')
        self.assertNotEqual(one,two)
        self.assertEqual(one,source_identity('https://reddit.com/r/codex/comments/abc/comment/first1/'))

    def test_github_comment_fragments_remain_distinct(self):
        self.assertNotEqual(source_identity('https://github.com/org/repo/issues/1#issuecomment-111'),source_identity('https://github.com/org/repo/issues/1#issuecomment-222'))
        self.assertNotEqual(source_identity('https://github.com/org/repo/pull/1#discussion_r111'),source_identity('https://github.com/org/repo/pull/1#discussion_r222'))

    def test_github_document_revisions_match(self):
        self.assertEqual(source_identity('https://github.com/Owner/Repo/blob/main/docs/guide.md'),source_identity('https://github.com/owner/repo/blob/abcd1234/docs/guide.md'))

    def test_github_different_documents_stay_distinct(self):
        self.assertNotEqual(source_identity('https://github.com/owner/repo/blob/main/one.md'),source_identity('https://github.com/owner/repo/blob/main/two.md'))

    def test_github_directory_readme_matches_snapshot(self):
        self.assertEqual(source_identity('https://github.com/cursor/plugins/tree/main/pstack'),source_identity('https://github.com/cursor/plugins/blob/1234/pstack/README.md'))

    def test_tracking_is_removed_but_meaningful_queries_remain(self):
        self.assertEqual(source_identity('https://example.com/article?id=1&utm_source=x#intro'),source_identity('https://example.com/article?id=1'))
        self.assertNotEqual(source_identity('https://example.com/article?id=1'),source_identity('https://example.com/article?id=2'))

if __name__=='__main__':
    unittest.main()
