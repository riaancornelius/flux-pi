__author__ = 'Riaan'

import requests, json

class JiraTicket(object):

    def __init__(self, key, status):
        self.key = key
        self.status = status

    def update_online(self):
        print 'update'
        # Do service call to update status

    def is_status(self, expected):
        return self.status == expected


class JiraTicketSearch(object):

    def __init__(self, tickets):
        print 'init'
        self.tickets = tickets

    def fetch(self):
        print 'Fetching...'
        jira_url = "https://projectflux.atlassian.net/rest/api/2/search"
        ticket_list = {"list" : ",".join(map(str, self.tickets))}
        data = {'jql':'key in (%(list)s)' % ticket_list}
        r = requests.get(jira_url, auth=('Flux', '3r#kWzEf!NEx'), params=data)
        print(r.url)
        response = r.json()
        issues = []
        for issue in response.get('issues'):
            try:
                key = issue.get('key')
                status = issue.get('fields').get('status').get('name')
                issues.append(JiraTicket(key, status))
                #print issue.get('key') + ': ' + issue.get('fields').get('status').get('name')
            except:
                print "Error in: " + issue
        return issues

        
#jira_url = "https://projectflux.atlassian.net/rest/api/2/search?jql=key%20in%20(FLUX-58%2CFLUX-57%2CFLUX-75%2CFLUX-53%2CFLUX-67%2CFLUX-60%2CFLUX-62)"

#data = json.dumps({'jql':'key in (FLUX-58,FLUX-57,FLUX-75,FLUX-53,FLUX-67,FLUX-60,FLUX-62)'})

#r = requests.post(jira_url, data, auth=('Flux', '3r#kWzEf!NEx'))

tickets = ['FLUX-58','FLUX-57','FLUX-75','FLUX-53','FLUX-67','FLUX-60','FLUX-62']
search = JiraTicketSearch(tickets)
issues = search.fetch()

for issue in issues:
    print issue.key + ': ' + issue.status + '  (done: ' + str(issue.is_status('Done')) +')'
