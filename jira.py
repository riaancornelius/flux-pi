__author__ = 'Riaan'

import requests, json

jira_url = "https://projectflux.atlassian.net/rest/api/2/"
jira_auth=('Flux', '3r#kWzEf!NEx')

class JiraTicket(object):

    def __init__(self, key, status):
        self.key = key
        self.status = status

    def update_online(self):
        print ''
        print 'Updating ' + self.key + ': ' + self.status
        headers = {'content-type': 'application/json'}
        url = jira_url + 'issue/' + self.key + '/transitions'

        data = {"transition": {"id":str(self.get_status_id())}}
        params = {'expand': 'transitions.fields'}

        try:
            response = requests.post(url, stream=True, params=params, data=json.dumps(data), headers=headers, auth=jira_auth)
            if response.status_code == 204:
                return True
            else:
                print response.text
                return False
        except:
            print 'Could not update issue: ' + self.key
            return False;

    def is_status(self, expected):
        return self.status == expected

    def get_status_id(self):
        if self.status == 'In Progress':
            return 11
        elif self.status == 'Done':
            return 151
        elif self.status == 'In Review':
            return 71
        else: #self.status == 'To Do':
            return 161


class JiraTicketSearch(object):

    def __init__(self, tickets):
        self.tickets = tickets

    def fetch(self):
        print 'Fetching ticket statuses...'
        ticket_list = {"list" : ",".join(map(str, self.tickets))}
        data = {'jql':'key in (%(list)s)' % ticket_list}
        issues = []
        try:
            r = requests.get(jira_url + "search", auth=jira_auth, params=data)
            response = r.json()
            for issue in response.get('issues'):
                try:
                    key = issue.get('key')
                    status = issue.get('fields').get('status').get('name')
                    issues.append(JiraTicket(key, status))
                    #print issue.get('key') + ': ' + issue.get('fields').get('status').get('name')
                except:
                    print "Error in: " + issue
        except:
            print 'Could not fetch tickets'
        return issues

if __name__ == "__main__":
    """
    tickets = ['FLUX-58','FLUX-57','FLUX-75','FLUX-53','FLUX-67','FLUX-60','FLUX-62']
    search = JiraTicketSearch(tickets)
    issues = search.fetch()

    for issue in issues:
        print issue.key + ': ' + issue.status + '  (done: ' + str(issue.is_status('Done')) +')'
    """
    print JiraTicket("FLUX-34", "In Progress").update_online()
