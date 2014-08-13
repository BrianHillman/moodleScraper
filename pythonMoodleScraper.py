import requests
import bs4
import os

folderPath = "test"
cookies = dict(MOODLEID1_DENTISTRY='%25C5c%2510%25BA%2581%252A',
               MoodleSessionDENTISTRY='rnc3bh90oo4pgmtqambmsksva5',
               MoodleSessionTestDENTISTRY='MRc1RM9jRm')


def getCourseMoogle(courseName):
    courseCode = courseName.split('-', 1)[0]

    response = requests.get('http://moodle.rutgers.edu/', cookies=cookies)
    #print "Resonse code:", response.status_code

    soup = bs4.BeautifulSoup(response.text)  #working to give html
    #print [x for x in soup.select("a")][0].attrs
    classLinks = [x for x in soup.select("a") if x.get('title') is not None]

    for ind, x in enumerate(classLinks):
        if courseCode in str(x.contents[0]):
            print  ind,') ', x.contents[0], "URL:", x.get('href')
    index = input("Enter a number: ")
    return classLinks[index].get('href')


def parseCourseMoogle(courseURL):
    response = requests.get(courseURL, cookies=cookies)
    print "Resonse code:", response.status_code
    soup = bs4.BeautifulSoup(response.text)
    bodyHeader = soup.find_all("h2", class_="headingblock header outline")
    print bodyHeader
    for x in bodyHeader[0].parents:
        if 'div' in x.name:
            pageBody = x

    pageBody = bodyHeader[0].parent
    weeks = pageBody.find_all("tr")
    for week in weeks:
        print parseWeek(week)


def parseWeek(tagTR):
    result = ""
    if tagTR.get('class') is not None and tagTR.get('id') is not None:
        if 'section separator' in tagTR.get('class'):
            return result
        #add week header to section output.
        result += str(tagTR.get('id')).replace("section-","Week ")
        result += "\n==============\n"
        weeksItems = tagTR.find_all('li')
        for x in weeksItems:
            result += handleLI(x)


    return result





#this is an example li
#
# <li class="activity forum" id="module-113162">
#  <a href="http://moodle.rutgers.edu/mod/forum/view.php?id=113162">
#   <img alt="" class="activityicon" src="http://moodle.rutgers.edu/mod/forum/icon.gif"/>
#    <span>
#     News forum
#    </span>
#  </a>
# </li>


def handleLI(tagLI):
    result =  "\n"
    result += str(tagLI)
    linkText = ""
    if tagLI.get_text() != None:
        linkText = tagLI.get_text()

    links =  tagLI.find_all('img')
    link = None
    fileType = None
    for link in links:
       # case plaintext, no link.
        if link is None:
            return "<div  font-family: 'Bitstream Vera Serif', georgia, times, serif;font-size: 12px>" + linkText + "</div>"

        fileType = str(link['src'])[str(link["src"]).rfind('/')+1:]

        if fileType != "spacer.gif":
            break


    if fileType == None:
        return ""
    elif fileType == "pdf.gif":
        fileName = downloadFile(getFileURL(tagLI))
    elif fileType == "word.gif":
        fileName = downloadFile(getFileURL(tagLI))
    elif fileType == "docx.gif":
        fileName = downloadFile(getFileURL(tagLI))
    elif fileType == "pptx.gif":
        fileName = downloadFile(getFileURL(tagLI))
    elif fileType == "powerpoint.gif":
        fileName = downloadFile(getFileURL(tagLI))
    #test downloading items marked with icon.gif
    elif fileType == "icon.gif":
        fileName = downloadFile(getFileURL(tagLI))
    else:
        print "Skipping unhandled filetype: ", fileType
        return ""


    #TODO
    if len(fileName) > 2:
        return '&nbsp;<a href="/CurrentCourse/' + fileName + '" target="_new">' + tagLI.get_text() + '&nbsp;</a><br />\n'
    else:
        return ""



def getFileURL(tagLI):
    pathPrefix = 'http://moodle.rutgers.edu/mod/resource/view.php?inpopup=true&id='
    pathPrefix += tagLI['id'].replace("module-",'')

    return pathPrefix


def downloadFile(moodleURL):
    #print "downloading...", moodleURL

    fileURL  = requests.get(moodleURL, cookies = cookies, allow_redirects = False)
    folder   = fileURL.url[fileURL.url.rfind('=')+1:]
    try:
        fileURL  = str(fileURL.headers['location'])
    except:
        return ""

    fileName = fileURL[fileURL.rfind('/')+1:]
    fileURL  = requests.get(fileURL, cookies = cookies)
    #hacky way to replace % escaped characters, well at least spaces haha
    fileName = fileName.replace("%20", " ")


    #print "downloading ",fileURL.url, "As: ", fileName
    try:
        open(folderPath+'/'+fileName, 'wb')
    except:
        os.mkdir(folderPath)

    with open(folderPath+'/'+fileName, 'wb') as writeFile:
        for chunk in fileURL.iter_content(512):
            writeFile.write(chunk)
    return fileName




if __name__ == '__main__':
    siteURL    = 'http://moodle.rutgers.edu/course/view.php?id=2692'
    folderPath = siteURL[siteURL.rfind('=')+1:]
    parseCourseMoogle(siteURL)
