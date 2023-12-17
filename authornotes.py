from html import unescape
import base64
import requests
from bs4 import BeautifulSoup as bs

from calibre_plugins.grauthornotes.config import prefs

def clear(author, db):
    ### Find Author and clear notes ###
    try:
        db.set_notes_for('authors', author[0], '')
        return "complete"
    except:
        return "skipped"

def notes(author, db, bgcolor, bordercolor, textcolor):
    ### Find Author and add notes from GR Bio ###
    for i in range(5):
    
        try:
            items = []
            titles = []
            aname = author[1].get('name')
            aname = aname.replace(' ', '%20')
            url = f'https://www.goodreads.com/book/author/{aname}'
            webdata = requests.get(url)
            soup = bs(webdata.text, "html.parser")
            authorName = soup.find( class_ = "authorName")
            if authorName == '':
                return "skipped"
            #Get Author bio
            biodiv = soup.find( class_ = "aboutAuthorInfo")
            biospans = biodiv.find_all( "span" )
            bio = ''
            if len(biospans) >= 1:
                bio = biospans[-1]

            
            #Get author info
            dataTitles = soup.find_all( class_ = "dataTitle")
            if len(dataTitles) == 0 and bio == '':
                return "skipped"
            dataItems = soup.find_all( class_ = "dataItem")
            imgdiv = soup.find( class_ = "leftContainer authorLeftContainer")
            imgurl = imgdiv.find( "img" )['src']
            imgdata = requests.get(imgurl)
            encoded_image = base64.b64encode(imgdata.content)
            finalimg = encoded_image.decode('utf-8')
            dataurl = f'data:image/jpeg;base64,{finalimg}'

            for t in dataTitles:
                titles.append(t.text.strip())
            for i in dataItems:
                freetext = i.find_all("span", {"id" : lambda L: L and L.startswith('freeText')})
                if len(freetext) > 1:
                    i = freetext[1].decode_contents()
                    items.append(i)
                else:
                    items.append(i.decode_contents().replace(f'href="/', f'href="https://www.goodreads.com/').strip())

            if titles[0] == "Born":
                textstr = dataTitles[0].next_sibling.strip()
                if len(titles) > len(items):
                    items.insert(0, textstr)
                elif len(titles) == len(items) and len(textstr) != 0:
                    items[0] = f'{textstr}; {items[0].strip()}'

            html = "<div>\r\n   <table border=\"0\" style=\"border-collapse: collapse\" cellspacing=\"2\" cellpadding=\"0\">\r\n      <thead>\r\n         <tr>\r\n            <td bgcolor=\"[bgcolor]\" style=\"vertical-align: middle; padding-left: 5; padding-right: 5; padding-top: 10; padding-bottom: 10; border-top: 1px; border-right: 1px; border-bottom: 1px; border-left: 1px; border-top-color: [bordercolor]; border-right-color: [bordercolor]; border-bottom-color: [bordercolor]; border-left-color: [bordercolor]; border-top-style: solid; border-right-style: solid; border-bottom-style: solid; border-left-style: solid\">\r\n               <h1 align=\"center\" style=\"margin-top: 18px; margin-bottom: 12px; margin-left: 0px; margin-right: 0px; text-indent: 0px; background-color: [bgcolor]\"><strong style=\"font-family: \'Arial\',\'sans-serif\'; font-size: xx-large; color: [textcolor]\">"
            html = f'{html}{authorName}</strong></h1>\r\n            </td>\r\n            <td bgcolor=\"[bgcolor]\" style=\"vertical-align: top; padding-left: 5; padding-right: 5; padding-top: 10; padding-bottom: 10; border-top: 1px; border-right: 1px; border-bottom: 1px; border-left: 1px; border-top-color: [bordercolor]; border-right-color: [bordercolor]; border-bottom-color: [bordercolor]; border-left-color: [bordercolor]; border-top-style: solid; border-right-style: solid; border-bottom-style: solid; border-left-style: solid\">\r\n               <p align=\"center\" style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; text-indent: 0px; background-color: [bgcolor]\"><img src=\"'
            html = f'{html}{dataurl}\" style=\"vertical-align: top\"></p>\r\n            </td>\r\n         </tr>\r\n      </thead>\r\n      <tbody>\r\n         '
            for c in range(len(titles)):
                html = f'{html}<tr>\r\n            <td bgcolor=\"[bgcolor]\" style=\"vertical-align: top; padding-left: 5; padding-right: 5; padding-top: 10; padding-bottom: 10; border-top: 1px; border-right: 1px; border-bottom: 1px; border-left: 1px; border-top-color: [bordercolor]; border-right-color: [bordercolor]; border-bottom-color: [bordercolor]; border-left-color: [bordercolor]; border-top-style: solid; border-right-style: solid; border-bottom-style: solid; border-left-style: solid\">\r\n               <p style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; text-indent: 0px; background-color: [bgcolor]\"><strong style=\"font-family: \'Arial\',\'sans-serif\'; font-size: 14px; color: [textcolor]; background-color: [bgcolor]\">{titles[c]}</strong></p>\r\n            </td>\r\n            <td bgcolor=\"[bgcolor]\" style=\"vertical-align: top; padding-left: 5; padding-right: 5; padding-top: 10; padding-bottom: 10; border-top: 1px; border-right: 1px; border-bottom: 1px; border-left: 1px; border-top-color: [bordercolor]; border-right-color: [bordercolor]; border-bottom-color: [bordercolor]; border-left-color: [bordercolor]; border-top-style: solid; border-right-style: solid; border-bottom-style: solid; border-left-style: solid\">\r\n               <p style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; text-indent: 0px; background-color: [bgcolor]\"><span style=\"font-family: \'Arial\',\'sans-serif\'; font-size: 14px; color: [textcolor]; background-color: [bgcolor]\">{items[c]}</span></p>\r\n            </td>\r\n         </tr>\r\n         '
            html = f'{html}<tr>\r\n            <td colspan=\"2\" bgcolor=\"[bgcolor]\" style=\"vertical-align: top; padding-left: 5; padding-right: 5; padding-top: 10; padding-bottom: 10; border-top: 1px; border-right: 1px; border-bottom: 1px; border-left: 1px; border-top-color: [bordercolor]; border-right-color: [bordercolor]; border-bottom-color: [bordercolor]; border-left-color: [bordercolor]; border-top-style: solid; border-right-style: solid; border-bottom-style: solid; border-left-style: solid\">\r\n               <p style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; text-indent: 0px; background-color: [bgcolor]\" id=\"freeTextContainerauthor23386367\"><span style=\"font-family: \'Arial\',\'sans-serif\'; font-size: 14px; color: [textcolor]\"></span><span style=\"font-family: \'Arial\',\'sans-serif\'; font-size: 14px; color: [textcolor]\">{bio}</span></p>\r\n            </td>\r\n         </tr>\r\n      </tbody>\r\n   </table>\r\n</div>'

            html = html.replace("[bgcolor]", bgcolor)
            html = html.replace("[bordercolor]", bordercolor)
            html = html.replace("[textcolor]", textcolor)
            db.import_note('authors', author[0], html, path_is_data=True)
            return "complete"
        except:
            pass
    return "skipped"