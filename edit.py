# -*- coding: utf-8 -*-
import argparse
import logging
import os
import sys

os.environ['PYWIKIBOT_DIR'] = os.path.dirname(os.path.realpath(__file__))
import pywikibot


class GererateSchoolList:
    def __init__(self, args):
        self.args = args

        self.site = pywikibot.Site()
        self.site.login()

        self.logger = logging.getLogger('generate_school_list')
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        self.logger.addHandler(stdout_handler)

    def replace_text_in_flags(self, text, flag1, flag2, ins):
        index1 = text.index(flag1)
        index2 = text.index(flag2)
        return text[:index1] + flag1 + ins + text[index2:]

    def main(self):
        pages = set()
        for page in pywikibot.Page(self.site, 'Template:Infobox school').embeddedin(namespaces=[0], filter_redirects=False):
            pages.add(page.title())
        for page in pywikibot.Page(self.site, 'Template:Infobox university').embeddedin(namespaces=[0], filter_redirects=False):
            pages.add(page.title())
        pages = sorted(pages)

        page_list = '''<!--
本列表由程式自動產生，任何手動修改將在下次更新時被覆蓋
程式碼：https://github.com/xiplus-mediawiki-programs/generate-school-list
-->
'''
        for page in pages:
            page_list += '# [[{}]]\n'.format(page)

        page = pywikibot.Page(self.site, 'Wikipedia:最近更改巡查/頁面列表/學校')
        old_text = page.text

        new_text = self.replace_text_in_flags(old_text, '<!-- list-start -->', '<!-- list-end -->', page_list)
        if old_text == new_text:
            self.logger.info('no changes')
            return

        new_text = self.replace_text_in_flags(new_text, '<!-- time-start -->', '<!-- time-end -->', '~~~~~')

        summary = '產生學校列表'

        if args.confirm or args.loglevel <= logging.DEBUG:
            pywikibot.showDiff(page.text, new_text)
            self.logger.info('summary: %s', summary)

        save = True
        if args.confirm:
            save = pywikibot.input_yn('Save changes?', 'Y')
        if save:
            self.logger.info('save changes')
            page.text = new_text
            page.save(summary=summary, minor=False)
        else:
            with open('out.txt', 'w', encoding='utf8') as f:
                f.write(new_text)
            self.logger.info('skip save')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--confirm', action='store_true')
    parser.add_argument('-d', '--debug', action='store_const', dest='loglevel', const=logging.DEBUG, default=logging.INFO)
    args = parser.parse_args()

    gsl = GererateSchoolList(args)
    gsl.logger.setLevel(args.loglevel)
    gsl.logger.debug('args: %s', args)
    gsl.main()
