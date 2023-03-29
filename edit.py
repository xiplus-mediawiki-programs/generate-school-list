# -*- coding: utf-8 -*-
import argparse
import logging
import os
import sys

os.environ['PYWIKIBOT_DIR'] = os.path.dirname(os.path.realpath(__file__))
import pywikibot

parser = argparse.ArgumentParser()
parser.add_argument('pagename', nargs='?')
parser.add_argument('-c', '--confirm', action='store_true')
parser.add_argument('-d', '--debug', action='store_const', dest='loglevel', const=logging.DEBUG, default=logging.INFO)
args = parser.parse_args()

logger = logging.getLogger('generate_school_list')
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)
logger.setLevel(args.loglevel)
logger.debug('args: %s', args)

site = pywikibot.Site()
site.login()

FLAG1 = '<!-- bot-start -->'
FLAG2 = '<!-- bot-end -->'

pages = set()
for page in pywikibot.Page(site, 'Template:Infobox school').embeddedin(namespaces=[0], filter_redirects=False):
    pages.add(page.title())
for page in pywikibot.Page(site, 'Template:Infobox university').embeddedin(namespaces=[0], filter_redirects=False):
    pages.add(page.title())
pages = sorted(pages)

page_list = ''
for page in pages:
    page_list += '# [[{}]]\n'.format(page)

page = pywikibot.Page(site, 'Wikipedia:最近更改巡查/頁面列表/學校')
INDEX1 = page.text.index(FLAG1)
INDEX2 = page.text.index(FLAG2)

new_text = page.text[:INDEX1] + FLAG1
new_text += '''<!--
本列表由程式自動產生，任何手動修改將在下次更新時被覆蓋
程式碼：https://github.com/xiplus-mediawiki-programs/generate-school-list
-->'''
new_text += '\n' + page_list + page.text[INDEX2:]

summary = '產生學校列表'

if args.confirm or args.loglevel <= logging.DEBUG:
    pywikibot.showDiff(page.text, new_text)
    logger.info('summary: %s', summary)

save = True
if args.confirm:
    save = pywikibot.input_yn('Save changes?', 'Y')
if save:
    logger.info('save changes')
    page.text = new_text
    page.save(summary=summary, minor=False)
else:
    with open('out.txt', 'w', encoding='utf8') as f:
        f.write(new_text)
    logger.info('skip save')
