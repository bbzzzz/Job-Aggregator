# Part 0 Preparation 
#-------------------------------------------------------------------------------------------------
import urllib2
from bs4 import BeautifulSoup
import pandas as pd

# Set up server on user's computer for OAuth 2.0 based authentication and authorization
# python -m SimpleHTTPServer
from linkedin import linkedin  # sudo pip install python-linkedin
import xmltodict    # sudo pip install xmltodict

# Get search terms from user input
key_words = raw_input("Key Words ---> ")            

seach_url_monster = '-'.join(key_words.split())     # Set search terms for Monster
search_url = '+'.join(key_words.split())            # Set search terms for Indeed and CareerBuilder
search_term = key_words                             # Set search terms for LinkedIn APIs

# create a dataframe of job listings from lists of the titles, companies, locations, and links
def createJobListingsDF(titles,companies,cities,states,links):
    jobDict = {
    'Title':titles,
    'Company':companies,
    'City':cities,
    'State':states,
    'Link':links
    }
    
    jobListings = pd.DataFrame(jobDict)
    return jobListings

# Part 1 Webscraping Monster.com
#-------------------------------------------------------------------------------------------------
#recursively scrape monster.com for jobs given a URL and starting page number 
#(default is 1) and output a dataframe of job listings

def getMonsterJobs(monsterURL,page=1,titles = [],companies = [],cities = [], states = [],links = []):  
    #define variable later used as a test to see if additional web pages
    #contain additional job listings   
    startLength = len(titles)    
    #scrape the website for job listings
    monsterPage = urllib2.urlopen(monsterURL+str(page))
    soup = BeautifulSoup(monsterPage)
    jobs = soup.findAll('table',{'class':'listingsTable'})
    #iterate through each job listing
    for job in jobs:
        titleBlocks = job.findAll('div',{'class':'jobTitleContainer'})
        for titleBlock in titleBlocks:
            #find all titles        
            title = str(titleBlock.text.strip())
            titles.append(title)
            #find all links        
            link = titleBlock.find('a')['href']
            links.append(link)
        #find all companies
        companyBlocks = job.findAll('div',{'class':'companyContainer'})    
        for companyBlock in companyBlocks:
            company = companyBlock.find('a')['title']
            companies.append(company)
        #find all locations
        locationBlocks = job.findAll('div',{'class':'jobLocationSingleLine'})
        for locationBlock in locationBlocks:
            try:
                location = locationBlock.find('a')['title']
            except TypeError:
                location = 'No location listed'
            city, space, state = location.partition(', ')            
            cities.append(city)
            states.append(state[:2])
    #test if web page added any new job listings or if it contained no new data
    #if no entries were added, end the web scraping; otherwise, scrape the next page
    endLength = len(titles)
    if endLength > startLength:
        page = page + 1
        getMonsterJobs(monsterURL,page)
    #create dataframe of monster.com jobs from lists of titles, companies, locations, and links
    monsterJobs = createJobListingsDF(titles,companies,cities,states,links)
    return monsterJobs
    
# Part 2 Webscraping Indeed.com    
#-------------------------------------------------------------------------------------------------
# generate a list with all page urls
def countIndeedJobs():    
    # combine base url with user-defined search terms
    # first page    
    baseUrl = 'http://www.indeed.com/jobs?q=' + search_url +'&filter=0&start='
    pagesUrl = urllib2.urlopen(baseUrl)
    soup = BeautifulSoup(pagesUrl)
    # get the total number of all pages    
    totalListings = int(soup.find('div', {'id':'searchCount'}).text[16:])
    pages = range(0, totalListings, 10)
    myUrls = []
    # generate urls for page 2 and above
    for apage in pages:
        myUrls.append(baseUrl + str(apage))
    return myUrls

# Parse webpage and return lists containing titles, companies, cities, states, and links
def getIndeedPage(aUrl):
    jobsPage = urllib2.urlopen(aUrl)
    soup = BeautifulSoup(jobsPage)
    jobs = soup.findAll('td',{'id':'resultsCol'})
    titles = []
    companies = []
    cities = []
    states = []
    links = []
    for job in jobs:
        titleBlocks = job.findAll('div',{'itemtype':'http://schema.org/JobPosting'})
        for titleBlock in titleBlocks:
            title = titleBlock.find('a')['title']
            titles.append(title)
            link = 'www.indeed.com' + titleBlock.find('a')['href']
            links.append(link)
        companyBlocks = job.findAll('span',{'itemtype':'http://schema.org/Organization'})            
        for companyBlock in companyBlocks:            
            company = companyBlock.get_text('span',{'itemprop':'name'})
            companies.append(company)
        locationBlocks = job.findAll('span',{'itemtype':'http://schema.org/Postaladdress'})            
        for locationBlock in locationBlocks:            
            location = locationBlock.get_text('span',{'itemprop':'addressLocality'})
            city, space, state = location.partition(', ')            
            cities.append(city)
            states.append(state[:2])
    return [titles,companies,cities,states,links]

# Iterate through all webpages and convert lists to dataframe
def getIndeedJobs(titles = [],companies = [],cities = [], states = [],links = []):
    myUrls = countIndeedJobs()
    for aUrl in myUrls:
        data = getIndeedPage(aUrl)
        titles = titles + data[0]
        companies = companies + data[1]
        cities = cities + data[2]
        states = states + data[3]
        links = links + data[4]
    allJobs = createJobListingsDF(titles,companies,cities,states,links)
    return allJobs

# Part 3 Webscraping CareerBuilder.com 
#-------------------------------------------------------------------------------------------------
CB_URL = 'http://www.careerbuilder.com/jobseeker/jobs/jobresults.aspx?IPath=QH&qb=1&s_rawwords=' + search_url +'&s_freeloc=&s_jobtypes=ALL&sc_cmp2=js_findjob_home&FindJobHomeButton=hptest_ignore2'
CB_Page = urllib2.urlopen(CB_URL)
soup = BeautifulSoup(CB_Page)

#find list of URLs for all pages after 1st page of search
nextpage = soup.findAll('td',{'class':'nav_btm_cell'})
other = soup.findAll('a',{'class':'JL_MXDLPagination2_next'})
for page in nextpage:
    link = page.find('a')['href']
    number = page.text.strip()
a = number[number.find('of ')+3:number.find(' |')-1]
totalPages= int(a)

baseURL = "http://www.careerbuilder.com/jobseeker/jobs/jobresults.aspx?excrit=st%3da%3buse%3dALL%3brawWords%3d"+ search_url +"%3bCID%3dUS%3bSID%3d%3f%3bTID%3d0%3bLOCCID%3dUS%3bENR%3dNO%3bDTP%3dDRNS%3bYDI%3dYES%3bIND%3dALL%3bPDQ%3dAll%3bPDQ%3dAll%3bPAYL%3d0%3bPAYH%3dgt120%3bPOY%3dNO%3bETD%3dALL%3bRE%3dALL%3bMGT%3dDC%3bSUP%3dDC%3bFRE%3d30%3bCHL%3dAL%3bQS%3dsid_unknown%3bSS%3dNO%3bTITL%3d0%3bOB%3d-relv%3bJQT%3dRAD%3bJDV%3dFalse%3bSITEENT%3dUSJob%3bMaxLowExp%3d-1%3bRecsPerPage%3d25&amp&pg="
#pagelinks is a list of all the URLs we need to scrape after the first page
pageLinks =[]
iterator=2
for iterator in range(2,totalPages):
    modifiedURL= baseURL+str(iterator)+'&IPath=QHKV'
    pageLinks.append(modifiedURL)
    
#function to scrape each page
def getCBJobs(CB_URL):
    CB_Page = urllib2.urlopen(CB_URL)
    soup = BeautifulSoup(CB_Page)
    jobs = soup.findAll('tr')
    titles = []
    links = []
    locations = []
    companies = []
    for job in jobs:
        titleBlocks = job.findAll('td',{'class':'jl_col2'})
        titleHead = job.findAll('a',{'class':'jt prefTitle'})
        #find all titles and remove missing values     
        for title in titleHead:
            titles.append(title.text)            
            titles = [x for x in titles if x != None]
        #find all links        
        for title in titleBlocks:        
            link = title.find('a')['href']
            links.append(link)
        #find all companies
        companyBlocks = job.findAll('td',{'class':'jl_col3'})
        for companyBlock in companyBlocks:
            company = companyBlock.findAll('strong')    
            company = str(companyBlock.text.strip())    
            companies.append(company)
        #find all locations
        locationBlocks = job.findAll('td',{'class':'jl_col4'})
        for locationBlock in locationBlocks:
            location = locationBlock.find('div',{'class':'jl_col4_div'})
            location = str(locationBlock.text.strip())
            locations.append(location)
    return titles,links,companies,locations

# Create list containing required information
Titles = []
Links = []
Companies = []
Locations = []
for aPage in pageLinks:
    CB_URL = aPage
    All = getCBJobs(CB_URL)
    Titles = Titles + (All[0])
    Links = Links + (All[1])
    Companies = Companies + (All[2])
    Locations = Locations +(All[3])

States = []
Cities = []
for location in Locations:
    state = location.split('-')[0].strip()
    States.append(state)
    city = location.split('-')[1].strip()
    Cities.append(city)
    
CBdict = {
            'Company': Companies,
            'Title':   Titles,
            'City':    Cities,
            'State':   States,
            'Link':    Links
        }

# Output as dataframe
CB_FinalDF = pd.DataFrame(CBdict)

# Part 4 Get job lists from LinkedIn API
#-------------------------------------------------------------------------------------------------
# Set token and secret for LinkedIn API - OAuth 1.0
CONSUMER_KEY = '758bcqo3nipdwk'
CONSUMER_SECRET = 'mUNd9c51xi5jDtlg'
USER_TOKEN = 'b86af9a8-1757-42de-a8cc-60acb6f61eb9'
USER_SECRET = 'af85d9ce-d082-4411-ad3b-1763e07a5ab2'
RETURN_URL = 'http://localhost:8000'

# Setup connection with LinkedIn
authentication = linkedin.LinkedInDeveloperAuthentication(CONSUMER_KEY, CONSUMER_SECRET, 
                                                          USER_TOKEN, USER_SECRET, 
                                                          RETURN_URL, linkedin.PERMISSIONS.enums.values())

application = linkedin.LinkedInApplication(authentication)

# get total number of available job titles
total = application.search_job(params={'keywords': search_term, 
                                       'start':0, 'count': 20, 'country-code':'us'})['numResults']
# Comment above line and uncomment following line if searching for specific job titles                                     
#total = application.search_job(params={'job-title': 'Data Scientist', 'start':0, 'count': 20, 'country-code':'us'})['numResults']
                                                                          
job_list = []
raw_job_list = []
start = 0

# Retrieve job information using LinkedIn Job Search API
for i in range(0,total+1,20):
        
    # Retrieve 20 jobs on every call to LinkedIn Job Search API and store in a list
    raw_job_list = application.search_job(params={'keywords': search_term, 
                                       'start':0, 'count': 20, 'country-code':'us'})                                      
    # Comment above line and uncomment following line if searching for specific job titles                                  
    #raw_job_list = application.search_job(params={'job-title': 'Data Scientist', 'start':i, 'count': 20, 'country-code':'us'})
                                         
    # Parse the list containing job information                                     
    for job in raw_job_list['jobs']['values']:
        term = []        
        # LinkedIn Job Search API return job ID instead of Job Title        
        term.append(job['id'])
        term.append(job['company']['name'])
        
        # Split location information into City and State        
        flag = 0
        if 'locationDescription' in job:
            location = job['locationDescription']
            
            flag = location.find(',')
            if flag > 0:
                city = location[0:flag]
                state = location[flag+2:len(location)]
            if flag < 0:
                city = location
                state = ''
            
            term.append(city)
            term.append(state)
                
        job_list.append(term)

# Retrieve job titles with LinkedIn Get Job API and job IDs
def get_job_title(job_id):
    
    # Send request to LinkedIn server using OAuth 2.0 based authentication     
    url = 'https://api.linkedin.com/v1/jobs/' + str(job_id) + '?oauth2_access_token=AQVIHZX39PPbvEC9mPzDPTVze3zuZvDp4BFGn9tGfnvb3GKXmgS_AKCRNT_y85nyb8f6HAWLIHIruJM5XVKGo5dAy7cbn5rEq0Zwt63D2D1BnpX-otZVvHvmxL8uJnfQDDeuZuL6sgVF8avXK88PAPJsY7i-qtqqSi35oBNSqWR_sy4oRwc'
    # read url
    file = urllib2.urlopen(url)
    data = file.read()
    file.close()
    # Parse returned xml file    
    data = xmltodict.parse(data)
    # Get job title corresponding to each job ID
    Job_title = data['job']['position']['title']
    
    return Job_title

for job in job_list:
    job.append(get_job_title(job[0]))

# Create list containing required information
Job_Title = [x[4] for x in job_list]
Company = [x[1] for x in job_list]
City = [x[2] for x in job_list]
State = [x[3] for x in job_list]
Link = ['http://www.linkedin.com/jobs?viewJob=&jobId='+str(x[0]) for x in job_list]

Job_Dict = {
                'Title':        Job_Title,
                'Company':      Company,
                'City':         City,
                'State':        State,
                'Link':         Link
            }

# Output as dataframe
Job_DF = pd.DataFrame(Job_Dict)
Job_DF_DD = Job_DF.drop_duplicates() 


# Part 5 Combine all parts together and output as csv
#-------------------------------------------------------------------------------------------------
#define the Monster URL of interest and actually run Monster code
monsterURL = 'http://jobsearch.monster.com/search/?q='+seach_url_monster+'&pg='
monsterJobs = getMonsterJobs(monsterURL)
print "Monster jobs: " + str(len(monsterJobs))
monsterJobs.to_csv('monsterJobs1.csv')

#actually run Indeed code 
indeedJobs = getIndeedJobs()
print "Indeed jobs: " + str(len(indeedJobs))
indeedJobs.to_csv('indeedJobs1.csv')

print "CareerBuilder jobs: " + str(len(CB_FinalDF))
print "LinkedIn jobs: " + str(len(Job_DF_DD))

allJobs = pd.concat([monsterJobs,indeedJobs,CB_FinalDF,Job_DF_DD], keys=['monster.com','indeed.com','careerbuilder.com','linkedin.com'])
print "Monster, Indeed, CareerBuilder, and LinkedIn jobs: " + str(len(allJobs))

allJobsRed=allJobs.drop_duplicates(cols=('Title','Company','City','State'))
print "Monster, Indeed, CareerBuilder, and LinkedIn jobs (no duplicates): " + str(len(allJobsRed))
print "Duplicates removed: " + str(len(allJobs)-len(allJobsRed))

allJobsRed.to_csv('allJobs.csv')
