from mwcleric.fandom_client import FandomClient
from mwcleric.auth_credentials import AuthCredentials
from mwcleric.template_modifier import TemplateModifierBase
from mwparserfromhell.nodes import Template
from mwparserfromhell.nodes.extras.parameter import Parameter
from runes_reforged_parser import RunesReforgedParser


credentials = AuthCredentials(user_file='bot')
site = FandomClient(wiki='lol', credentials=credentials)
summary = "correct primary rune tree"

rune_parser = RunesReforgedParser()

class TemplateModifier(TemplateModifierBase):
    def update_template(self, template: Template):
        fp = self.data['fp']
        if not template.has('runes'):
            return
        param = template.get('runes')
        param: Parameter
        w = param.value
        sss = []
        for tl in w.filter_templates():
            tl: Template
            rune_names = tl.get('1').value.strip()
            current = '-'
            if template.has('primary'):
                current = template.get('primary').value.strip()
            correct = '-'
            primary = rune_parser.get_primary(rune_names)
            if primary is not None:
                correct = primary
            sss.append(current+'\t'+correct+'\t'+rune_names+'\t'+self.current_page.name)
        fp.write('\n'.join(sss) + '\n')
        return

def wtf():
    with open('rune-names.txt', 'w') as fp:
        TemplateModifier(
            site, 'Scoreboard/Player',
            page_list=site.pages_using('Scoreboard/Player/Runes'),
            summary=summary,
            quiet=True, # Shhhhh
            data={
                'fp': fp,
            }).run()

def find_discrepancies():
    import csv

    fmt = '    {{current="{:s}", correct="{:s}", runes="{:s}"}},'

    bad_pages = set()
    print('{')
    with open('rune-names.txt', 'r') as fp:
        reader = csv.reader(fp, delimiter='\t')
        for row in reader:
            current, correct, runes, page_name = row
            if current in ('-', correct): continue
            primary = rune_parser.get_primary(runes)
            assert(primary == correct)
            bad_pages.add(page_name)
            print(fmt.format(current, correct, runes))
    print('}')
    return list(bad_pages)


class BadPagesTemplateModifier(TemplateModifierBase):
    def update_template(self, template: Template):
        if not template.has('primary'):
            return
        if not template.has('runes'):
            return
        param = template.get('runes')
        param: Parameter
        w = param.value
        sss = []
        for tl in w.filter_templates():
            tl: Template
            rune_names = tl.get('1').value.strip()
            current = template.get('primary').value.strip()
            primary = rune_parser.get_primary(rune_names)
            if primary is not None and current != primary:
                template.add('primary', primary,
                             before='secondary')
        return

def fix_bad_pages(bad_pages):
    BadPagesTemplateModifier(
        site, 'Scoreboard/Player',
        title_list=bad_pages,
        summary=summary,
        lag=10).run()


bad_pages = find_discrepancies()

### I'm afraid of running this atm, lol. Need more tests.
# fix_bad_pages(bad_pages)