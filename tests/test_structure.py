"""Contracts that previously allowed silent editorial or release mistakes."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from site_builder.content import read_content, select_home_content, validate_case_studies
from site_builder.release import release_origin, check_release_output
from site_builder.templates.case import shell_lab
from site_builder.templates.taxonomy import validate_taxonomy

ROOT = Path(__file__).resolve().parents[1]


class StructureTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((ROOT / 'public-content/manifest.json').read_text())
        self.works = read_content(ROOT, self.manifest, 'work')
        self.posts = read_content(ROOT, self.manifest, 'writing')

    def test_home_selection_survives_allowlist_reordering(self):
        config = json.loads((ROOT / 'public-content/home.json').read_text())
        expected = select_home_content(config, self.works, self.posts)
        self.assertEqual(expected, select_home_content(config, self.works[::-1], self.posts[::-1]))
        for invalid in ('unknown-project', config['featured_work']):
            with self.subTest(slug=invalid), self.assertRaises(ValueError):
                select_home_content({**config, 'work': [invalid]}, self.works, self.posts)

    def test_case_scenarios_reorder_and_expand_without_mismatch(self):
        work = copy.deepcopy(next(item for item in self.works if item.get('case_study')))
        study = work['case_study']
        study['steps'].reverse()
        extra = {**study['steps'][0], 'id': 'extra', 'text': '第四条说明', 'nodes': ['第四条节点']}
        study['steps'].append(extra)
        validate_case_studies([work])
        html = shell_lab(study)
        self.assertEqual(html.count('class="scenario-panel"'), 4)
        for step in study['steps']:
            panel = html.split(f'data-scenario="{step["id"]}"', 1)[1].split('</section>', 1)[0]
            self.assertIn(step['text'], panel)
            self.assertTrue(all(node in panel for node in step['nodes']))
        study['steps'].append(extra)
        with self.assertRaises(ValueError):
            validate_case_studies([work])

    def test_topic_cannot_shadow_all_filter(self):
        taxonomy = json.loads((ROOT / 'public-content/taxonomy.json').read_text())
        topics = read_content(ROOT, self.manifest, 'topics')
        topics[0]['slug'] = 'all'
        with self.assertRaises(ValueError):
            validate_taxonomy(taxonomy, self.posts, topics)

    def test_release_rejects_preview_origins_and_demo_output(self):
        for origin in (None, 'http://127.0.0.1:4173', 'https://127.0.0.1', 'https://192.168.1.1',
                       'https://preview.local', 'https://example.com', 'https://site.org/path',
                       'https://user:secret@site.org', 'https://site.org/?q=1'):
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                release_origin({'site_url': origin})
        config = {'site_url': 'https://offset-site.org/'}  # Synthetic validation fixture; never published.
        self.assertEqual(release_origin(config), 'https://offset-site.org')
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            (output / 'index.html').write_text('test')
            check_release_output(output, config)
            (output / 'demos').mkdir()
            with self.assertRaises(ValueError):
                check_release_output(output, config)


if __name__ == '__main__':
    unittest.main()
