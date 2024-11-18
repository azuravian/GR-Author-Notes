import base64
import contextlib
import re
import json
import logging

from calibre_plugins.grauthornotes.config import prefs  # type: ignore
from calibre_plugins.grauthornotes.trans import translate, translate_list  # type: ignore
from calibre_plugins.grauthornotes.unzip import install_chrome  # type: ignore

import requests
from bs4 import BeautifulSoup as bs

logging.basicConfig(level=logging.INFO)

def link(author: tuple, db) -> str:
    alink = ''
    books = db.books_for_field('authors', author[0])
    for book in books:
        mi = db.get_metadata(book)
        url = get_book_url(mi)
        if not url:
            continue
        logging.info('url: %s', url)
        try:
            gr_authors = get_booksoup(url)
        except requests.RequestException as e:
            logging.error('Failed to get book soup: %s', e)
            continue

        aname = ''.join(get_aname(author).split()).replace("'", "&apos;")
        logging.info('aname: %s', aname)
        for a in gr_authors:
            clname = ''.join(a.get('name').split())
            logging.info('clname: %s', clname)
            if aname.lower() != clname.lower():
                logging.info('%s is not the same as %s', aname, clname)
                continue
            else:
                logging.info('%s is the same as %s', aname, clname)
                alink = a.get('url')
        if alink:
            break

    if alink:
        aval = {author[1].get('name'): alink}
        db.set_link_map('authors', aval, True)
        return alink
    else:
        return ''

def clear(author, db):
    ### Find Author and clear notes ###
    try:
        db.set_notes_for('authors', author[0], '')
        return True
    except Exception:
        return False

def notes(author, db, bgcolor, bordercolor, textcolor, author_link):
    ### Find Author and add notes from GR Bio ###
    for _ in range(5):
        with contextlib.suppress(Exception):
            
            try:
                url = ''
                if author_link != '':
                    url = author_link
                elif not prefs['only_confirmed']:
                    url = get_author_url(author)
                if not url:
                    return False
                #Get BeautifulSoup object
                soup = get_soup(url)
                #open('D:\\testa.xml','w').write(soup.prettify ())
            except Exception as e:
                print("Soup Error: ", e)

            #Get authorName
            authorName = soup.find(class_ = "authorName")
            if authorName == '':
                return False

            try:
                #Get Author bio
                bio = get_bio(soup)
            except Exception as e:
                print("Bio Error: ", e)

            #Get dataTitles
            dataTitles = soup.find_all(class_ = "dataTitle")
            if len(dataTitles) == 0 and bio == '':
                return False
            titles = [t.text.strip() for t in dataTitles]
            

            #Get dataItems
            dataItems = soup.find_all(class_ = "dataItem")
            try:
                items = items_list(dataItems)
            except Exception:
                print("Items_List error")
            try:
                items = fix_items(items, dataTitles, titles)
            except Exception:
                print("fix_items error")

            #Get author image
            try:
                dataurl = get_author_image(soup)
            except Exception:
                print("get image error")

            #Translate
            if prefs['translate']:
                lang = prefs['language']
                bio = translate(bio, lang)
                titles = translate_list(titles, lang)
                items = translate_list(items, lang)

            #Generate html
            try:
                html = gen_html(authorName, bio, titles, items, dataurl)
                html = html_color(bgcolor, bordercolor, textcolor, html)
            except Exception:
                print("html error")

            #Set author note
            try:
                db.import_note('authors', author[0], html, path_is_data=True)
                return True
            except Exception:
                return False
    return False

def gen_html(authorName, bio, titles, items, dataurl):
    html = "<div>\r\n   <table border=\"0\" style=\"border-collapse: collapse\" cellspacing=\"2\" cellpadding=\"0\">\r\n      <thead>\r\n         <tr>\r\n            <td bgcolor=\"[bgcolor]\" style=\"vertical-align: middle; padding-left: 5; padding-right: 5; padding-top: 10; padding-bottom: 10; border-top: 1px; border-right: 1px; border-bottom: 1px; border-left: 1px; border-top-color: [bordercolor]; border-right-color: [bordercolor]; border-bottom-color: [bordercolor]; border-left-color: [bordercolor]; border-top-style: solid; border-right-style: solid; border-bottom-style: solid; border-left-style: solid\">\r\n               <h1 align=\"center\" style=\"margin-top: 18px; margin-bottom: 12px; margin-left: 0px; margin-right: 0px; text-indent: 0px; background-color: [bgcolor]\"><strong style=\"font-family: \'Arial\',\'sans-serif\'; font-size: xx-large; color: [textcolor]\">"
    html = f'{html}{authorName}</strong></h1>\r\n            </td>\r\n            <td bgcolor=\"[bgcolor]\" style=\"vertical-align: top; padding-left: 5; padding-right: 5; padding-top: 10; padding-bottom: 10; border-top: 1px; border-right: 1px; border-bottom: 1px; border-left: 1px; border-top-color: [bordercolor]; border-right-color: [bordercolor]; border-bottom-color: [bordercolor]; border-left-color: [bordercolor]; border-top-style: solid; border-right-style: solid; border-bottom-style: solid; border-left-style: solid\">\r\n               <p align=\"center\" style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; text-indent: 0px; background-color: [bgcolor]\"><img src=\"'
    html = f'{html}{dataurl}\" style=\"vertical-align: top\"></p>\r\n            </td>\r\n         </tr>\r\n      </thead>\r\n      <tbody>\r\n         '
    for c in range(len(titles)):
        html = f'{html}<tr>\r\n            <td bgcolor=\"[bgcolor]\" style=\"vertical-align: top; padding-left: 5; padding-right: 5; padding-top: 10; padding-bottom: 10; border-top: 1px; border-right: 1px; border-bottom: 1px; border-left: 1px; border-top-color: [bordercolor]; border-right-color: [bordercolor]; border-bottom-color: [bordercolor]; border-left-color: [bordercolor]; border-top-style: solid; border-right-style: solid; border-bottom-style: solid; border-left-style: solid\">\r\n               <p style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; text-indent: 0px; background-color: [bgcolor]\"><strong style=\"font-family: \'Arial\',\'sans-serif\'; font-size: 14px; color: [textcolor]; background-color: [bgcolor]\">{titles[c]}</strong></p>\r\n            </td>\r\n            <td bgcolor=\"[bgcolor]\" style=\"vertical-align: top; padding-left: 5; padding-right: 5; padding-top: 10; padding-bottom: 10; border-top: 1px; border-right: 1px; border-bottom: 1px; border-left: 1px; border-top-color: [bordercolor]; border-right-color: [bordercolor]; border-bottom-color: [bordercolor]; border-left-color: [bordercolor]; border-top-style: solid; border-right-style: solid; border-bottom-style: solid; border-left-style: solid\">\r\n               <p style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; text-indent: 0px; background-color: [bgcolor]\"><span style=\"font-family: \'Arial\',\'sans-serif\'; font-size: 14px; color: [textcolor]; background-color: [bgcolor]\">{items[c]}</span></p>\r\n            </td>\r\n         </tr>\r\n         '
    html = f'{html}<tr>\r\n            <td colspan=\"2\" bgcolor=\"[bgcolor]\" style=\"vertical-align: top; padding-left: 5; padding-right: 5; padding-top: 10; padding-bottom: 10; border-top: 1px; border-right: 1px; border-bottom: 1px; border-left: 1px; border-top-color: [bordercolor]; border-right-color: [bordercolor]; border-bottom-color: [bordercolor]; border-left-color: [bordercolor]; border-top-style: solid; border-right-style: solid; border-bottom-style: solid; border-left-style: solid\">\r\n               <p style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; text-indent: 0px; background-color: [bgcolor]\" id=\"freeTextContainerauthor23386367\"><span style=\"font-family: \'Arial\',\'sans-serif\'; font-size: 14px; color: [textcolor]\"></span><span style=\"font-family: \'Arial\',\'sans-serif\'; font-size: 14px; color: [textcolor]\">{bio}</span></p><p align=\"right\" style=\"margin-top: 12px; margin-bottom: 12px; margin-left: 0px; margin-right: 0px; text-indent: 0px; background-color: #242424\"><span style=\"font-family: \'Arial\',\'sans-serif\'; font-size: 8px; color: #ffffff; background-color: #242424\">Generated using the GR Author Notes plugin</span></p>\r\n            </td>\r\n         </tr>\r\n      </tbody>\r\n   </table>\r\n</div>'
    return html

def html_color(bgcolor, bordercolor, textcolor, html):
    html = html.replace("[bgcolor]", bgcolor)
    html = html.replace("[bordercolor]", bordercolor)
    html = html.replace("[textcolor]", textcolor)
    return html

def get_aname(author: tuple) -> str:
    pattern = re.compile('editor', re.IGNORECASE)
    aname = author[1].get('name')
    aname = pattern.sub('', aname)
    return aname.replace('()', '').strip()

def get_author_image(soup):
    imgdiv = soup.find( class_ = "leftContainer authorLeftContainer")
    imgurl = imgdiv.find( "img" )['src']
    imgdata = requests.get(imgurl)
    encoded_image = base64.b64encode(imgdata.content)
    finalimg = encoded_image.decode('utf-8')
    return f'data:image/jpeg;base64,{finalimg}'

def get_bio(soup):
    biodiv = soup.find( class_ = "aboutAuthorInfo")
    #open('D:\\testd.xml','w').write(biodiv.prettify ())
    biospans = biodiv.find_all( "span" )
    #print (biospans[-1])
    #print (len (biospans))
    return biospans[-1] if len(biospans) >= 1 else ''

def get_author_url(author):
    aname = get_aname(author)
    aname = aname.replace(' ', '%20')
    return f'https://www.goodreads.com/book/author/{aname}'

def set_author_link(author, link, db):
    return

def get_soup(url):
    webdata = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"})
    return bs(webdata.text, "html.parser")

def get_booksoup(url: str):
    soup = get_soup(url)
    book_dict = {}
    for script in soup.find_all("script",type="application/ld+json"):
        book_dict = json.loads(script.contents[0])
    return book_dict.get('author') if book_dict else {}


def items_list(dataItems):
    items = []
    for i in dataItems:
        freetext = i.find_all("span", {"id" : lambda L: L and L.startswith('freeText')})
        if len(freetext) > 1:
            i = freetext[1].decode_contents()
        else:
            i = i.decode_contents().replace('href="/', 'href="https://www.goodreads.com/').strip()
        items.append(i)
    return items

def get_book_url(mi) -> str:
    ids = mi.identifiers
    goodreads = ids.get('goodreads')
    isbn = ids.get('isbn')
    amazon = ids.get('amazon')
    if goodreads:
        return f'https://www.goodreads.com/book/show/{goodreads}'
    elif isbn:
        return f'https://www.goodreads.com/book/isbn/{isbn}'
    elif amazon:
        return f'https://www.goodreads.com/book/isbn/{amazon}'
    else:
        return ''

def fix_items(items, dataTitles, titles):
    if titles[0] == "Born":
        textstr = dataTitles[0].next_sibling.strip()
        if len(titles) > len(items):
            items.insert(0, textstr)
        elif len(titles) == len(items) and len(textstr) != 0:
            items[0] = f'{textstr}; {items[0].strip()}'
    return items