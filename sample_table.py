import os

import datapane as dp
import pandas as pd
from dotenv import load_dotenv
from github import Github, UnknownObjectException

# get tokens
load_dotenv()
token = os.environ.get("GITHUB_API_TOKEN")
dp_token = os.environ.get("DATAPANE_TOKEN")

# get user profile data
username = 'clissa'
gh = Github(token)
user = gh.get_user(username)

# initialize empty dataframe for repos data
colnames = ['languages', 'topics', 'description', 'commits', 'collaborators', 'forks', 'stargazers', 'open_issues',
            'visibility', 'license']
repos_df = pd.DataFrame(data={}, columns=colnames)
repos_df.index.name = 'repository'

# loop through repos to get infos
for repo in user.get_repos():
    try:
        license = repo.get_license().raw_data['license']['name']
    except UnknownObjectException:  # github.GithubException.UnknownObjectException:
        license = None
    repos_df.loc[repo.name] = [repo.get_languages(), repo.get_topics(), repo.description, repo.get_commits().totalCount,
                               repo.get_collaborators().totalCount, repo.forks, repo.stargazers_count,
                               repo.open_issues_count, 'Private' if repo.private else 'Public', license
                               ]

report = dp.Report(
    # sample table
    dp.DataTable(repos_df.sort_values('stargazers', ascending=False), caption="User repositories")#
)

# save and open to visualize output
report.save(path='report.html', open=True)

# upload report
dp.login(token=dp_token)
report.upload(name="DataTable", #project='github_dashboard',
              description='Sample table of most starred repositories.', publicly_visible=True)