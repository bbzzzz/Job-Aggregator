import urllib2
from bs4 import BeautifulSoup
import pandas as pd
from linkedin import linkedin  # sudo pip install python-linkedin
import xmltodict    # sudo pip install xmltodict

# to set up server on user's computer for OAuth 2.0 based authentication and authorzation
# Uncomment below line
# python -m SimpleHTTPServer


#----------------------------Define Functions----------------------------

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


#---------------------------- Webscraping Monster.com ----------------------------

# recursively scrape monster.com for jobs given a URL and starting page number 
# (default is 1) and output a dataframe of job listings
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
    
#---------------------------- Webscraping Indeed.com ---------------------------- 
# generate a list with all page urls
def countIndeedJobs(search_url):    
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

# Parse webpage and return lists containing titles, companies, cities, states and links
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

# Convert list to dataframe
def getIndeedJobs(titles = [],companies = [],cities = [], states = [],links = []):
    myUrls = countIndeedJobs()
    for aUrl in myUrls:
        data = getIndeedPage(aUrl)
        titles = titles + data[0]
        companies = companies + data[1]
        cities = cities + data[2]
        states = states + data[3]
        links = links + data[4]
    # Create dataframe from 
    allJobs = createJobListingsDF(titles,companies,cities,states,links)
    return allJobs

#---------------------------- Using LinkedIn API ----------------------------

# Retrieve job titles with LinkedIn-Get-Job API and job IDs
def get_job_title(job_id):
    
    # Send request LinkedIn server using OAuth 2.0 based authentication     
    url = 'https://api.linkedin.com/v1/jobs/' + str(job_id) + '?oauth2_access_token=AQVIHZX39PPbvEC9mPzDPTVze3zuZvDp4BFGn9tGfnvb3GKXmgS_AKCRNT_y85nyb8f6HAWLIHIruJM5XVKGo5dAy7cbn5rEq0Zwt63D2D1BnpX-otZVvHvmxL8uJnfQDDeuZuL6sgVF8avXK88PAPJsY7i-qtqqSi35oBNSqWR_sy4oRwc'
    # read url
    file = urllib2.urlopen(url)
    data = file.read()
    file.close()
    # Parse returned xml file    
    data = xmltodict.parse(data)
    # Get job titile corresponding to each job ID    
    Job_title = data['job']['position']['title']
    
    return Job_title

def getLinkedinJobs(search_term,start=0):

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
    
    # get total number of available jobtitles
    total = application.search_job(params={'keywords': search_term, 
                                           'start':0, 'count': 20, 'country-code':'us'})['numResults']
    # Comment above line and uncomment following line if search for specific job titles                                     
    #total = application.search_job(params={'job-title': 'Data Scientist', 'start':0, 'count': 20, 'country-code':'us'})['numResults']
                                                                              
    job_list = []
    raw_job_list = []
    
    # Retrieve job informations using LinkedIn Job Search API
    for i in range(0,total+1,20):
            
        # Retrieve 20 jobs on every call to LinkedIn Job Search API and store in a list
        raw_job_list = application.search_job(params={'keywords': search_term, 
                                           'start':0, 'count': 20, 'country-code':'us'})                                      
        # Comment above line and uncomment following line if search for specific job titles                                  
        #raw_job_list = application.search_job(params={'job-title': 'Data Scientist', 'start':i, 'count': 20, 'country-code':'us'})
                                             
        # Parse the list containing job information                                     
        for job in raw_job_list['jobs']['values']:
            term = []        
            # LinkedIn Job Search API return job ID instead of Job Title        
            term.append(job['id'])
            term.append(job['company']['name'])
            # Split location information to City and State        
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
    
    for job in job_list:
        job.append(get_job_title(job[0]))
    
    # Create list containing required information
    titles = [x[4] for x in job_list]
    companies = [x[1] for x in job_list]
    cities = [x[2] for x in job_list]
    states = [x[3] for x in job_list]
    links = ['http://www.linkedin.com/jobs?viewJob=&jobId='+str(x[0]) for x in job_list]
    
    linkedinJobs = createJobListingsDF(titles,companies,cities,states,links).drop_duplicates()
    
    return linkedinJobs


# Combine all parts together and output as csv
#-------------------------------------------------------------------------------------------------
def main():
    # Get search terms from user input
    key_words = raw_input("KeY Words ---> ")            
    
    seach_url_monster = '-'.join(key_words.split())     # Set seeacr terms for Monster
    search_url_indeed = '+'.join(key_words.split())     # Set search terms for Indeed
    search_term_linkedin = key_words                    # Set search terms for LinkedIn APIs
    
    #define the Monster URL of interest and actually run Monster code
    monsterURL = 'http://jobsearch.monster.com/search/?q='+seach_url_monster+'&pg='
    monsterJobs = getMonsterJobs(monsterURL)
    print "Monster jobs: " + str(len(monsterJobs))
    monsterJobs.to_csv('monsterJobs1.csv')
    
    #actually run Indeed code 
    indeedJobs = getIndeedJobs(search_url_indeed)
    print "Indeed jobs: " + str(len(indeedJobs))
    indeedJobs.to_csv('indeedJobs1.csv')
    
    linkedinJobs = getLinkedinJobs(search_term_linkedin)
    print "LinkedIn jobs: " + str(len(linkedinJobs))
    linkedinJobs.to_csv('linkedinJobs1.csv')
    
    allJobs = pd.concat([monsterJobs,indeedJobs, linkedinJobs], keys=['monster.com','indeed.com','linkedin.com'])
    print "Monster, Indeed and LinkedIn jobs: " + str(len(allJobs))
    
    allJobsRed=allJobs.drop_duplicates(cols=('Title','Company','City','State'))
    print "Monster, Indeed, and LinkedIn jobs (no duplicates): " + str(len(allJobsRed))
    print "Duplicates removed: " + str(len(allJobs)-len(allJobsRed))
    
    allJobsRed.to_csv('allJobs1.csv')

if __name__ == "__main__":
    main()