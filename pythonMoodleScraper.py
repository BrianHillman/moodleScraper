import requests
import bs4
import os

folderPath = "test"
cookies = {}

def login():

    login = {"username":"*****", "password":"*****", "Content-Type":"application/x-www-form-urlencoded"}
    r = requests.post("https://moodle.rutgers.edu/login/index.php",params=login)

    cookie1 =  r.headers['set-cookie'].split(' ')[2].replace(';','')
    cookie1 = cookie1.split('=')

    cookie2 =  r.headers['set-cookie'].split(' ')[0].replace(';','')
    cookie2 = cookie2.split('=')

    cookies["MOODLEID1_DENTISTRY"] = "%25C5c%2510%25BA%2581%252A"
    cookies[cookie1[0]] = cookie1[1]
    cookies[cookie2[0]] = cookie2[1]

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
        print parseWeek(week).encode('utf-8')


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
    elif fileType == 'folder.gif':
        return downloadFolder(getFileURL(tagLI))
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
    #http://moodle.rutgers.edu/mod/resource/view.php?id=175920
    #
    #


    fileURL  = requests.get(moodleURL, cookies = cookies, allow_redirects = False)
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

def downloadFolder(url):
    print url
    response = requests.get(url, cookies=cookies)
    soup = bs4.BeautifulSoup(response.text)

    listOfFiles = soup.find("table", class_="files")
    try:
        listOfFiles = listOfFiles.find_all("a")
    except:
        return ""
    result = '<blockquote style="margin: 0px 0px 0px 40px; border: none; padding: 0px;">'
    for aTAg in listOfFiles:
            imgTag = aTAg.find('img')
            fileType = str(imgTag['src'])[str(imgTag["src"]).rfind('/')+1:]
            fileURL = aTAg['href']

            if fileType == "folder.gif":
                result += downloadFolder("http://moodle.rutgers.edu/mod/resource/"+str(fileURL))
                continue

            fileURL = aTAg['href']
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
            result += '&nbsp;<a href="/CurrentCourse/' + fileName + '" target="_new">' + aTAg.get_text() + '&nbsp;</a><br />\n'


    return result + '</blockquote>'


if __name__ == '__main__':
    #login()
    #print cookies
    cookies['MOODLEID1_DENTISTRY'] = "%25C5c%2510%25BA%2581%252A"
    cookies['MoodleSessionDENTISTRY'] = "91ea3r8l29g72psr6n2t0f5es0"
    cookies['MoodleSessionTestDENTISTRY'] = 'XEbJybtYNu'
    siteURL    = 'http://moodle.rutgers.edu/course/view.php?id='
    mCode = str(input("Enter the 4 digit course moodle code: "))
    siteURL += mCode
    folderPath = siteURL[siteURL.rfind('=')+1:]
    parseCourseMoogle(siteURL)


    # testing folders
