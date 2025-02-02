from prelims import Post

from unittest import TestCase
import tempfile


content = """
---
aaa: xxx
bbb: [xxx]
---

Hello world.
"""

content_draft = """
---
aaa: yyy
bbb: yyy
draft: true
---

This is draft content to be ignored.
"""


class PostTestCase(TestCase):

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.mdfile = tempfile.NamedTemporaryFile(suffix='.md',
                                                  dir=self.dir.name)
        self.mdfile.write(content.encode('utf-8'))
        self.mdfile.seek(0)
        self.mdfile_draft = tempfile.NamedTemporaryFile(suffix='.md',
                                                        dir=self.dir.name)
        self.mdfile_draft.write(content_draft.encode('utf-8'))
        self.mdfile_draft.seek(0)

    def tearDown(self):
        self.mdfile.close()
        self.mdfile_draft.close()
        self.dir.cleanup()

    def test_load(self):
        post = Post.load(self.mdfile.name)
        self.assertEqual(post.path, self.mdfile.name)
        self.assertEqual(post.front_matter, {'aaa': 'xxx', 'bbb': ['xxx']})
        self.assertEqual(post.raw_content, content)
        self.assertEqual(post.content, 'Hello world.')

    def test_is_draft(self):
        post = Post.load(self.mdfile.name)
        self.assertFalse(post.is_draft())
        post_draft = Post.load(self.mdfile_draft.name)
        self.assertTrue(post_draft.is_draft())

    def test_is_valid(self):
        post = Post.load(self.mdfile.name)
        self.assertTrue(post.is_valid())
        post_draft = Post.load(self.mdfile_draft.name)
        self.assertFalse(post_draft.is_valid())

    def test_update(self):
        post = Post.load(self.mdfile.name)

        post.update('aaa', 'zzz', allow_overwrite=False)
        post.update('bbb', ['zzz'], allow_overwrite=True)
        post.update('foo', 'bar')

        self.assertEqual(post.path, self.mdfile.name)
        self.assertEqual(post.front_matter,
                         {'aaa': 'xxx', 'bbb': ['zzz'], 'foo': 'bar'})

    def test_save(self):
        post = Post.load(self.mdfile.name)
        post.update('foo', 'bar')
        post.save()

        expected_content = """
---
aaa: xxx
bbb: [xxx]
foo: bar
---

Hello world.
"""

        self.assertEqual(self.mdfile.read().decode(), expected_content)
