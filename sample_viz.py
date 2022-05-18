import os

import altair as alt
import datapane as dp
import numpy as np
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

# highlights tab
received_stars = repos_df.stargazers.sum()


# languages tab
def get_languages_pct(repo_languages: dict) -> dict:
    total = sum(repo_languages.values())
    return {k: v / total for k, v in repo_languages.items()}


def get_languages_total(user_languages: pd.Series) -> dict:
    languages_dict = {}
    for repo_languages in user_languages:
        for k, v in repo_languages.items():
            languages_dict[k] = languages_dict.get(k, 0) + v
    return languages_dict


user_languages = get_languages_total(repos_df.languages)
user_languages_pct = get_languages_pct(user_languages)

source_bar = pd.DataFrame(
    {'language': user_languages.keys(), 'code lines': [np.log(x) for x in user_languages.values()]})
bar_chart = alt.Chart(source_bar).mark_bar().encode(
    x='code lines:Q',
    y=alt.Y('language:O', sort='-x'),
    tooltip=['language', 'code lines'],
).interactive()

source_donut = pd.DataFrame({'language': user_languages_pct.keys(), 'pct': user_languages_pct.values()})
source_donut.sort_values('pct', ascending=False, inplace=True)
donut_chart = alt.Chart(source_donut).mark_arc(innerRadius=45).encode(
    theta=alt.Theta(field='pct', type='quantitative'),
    color=alt.Color(field='language', type='nominal'),
    tooltip=['language', 'pct'],
).interactive()

report = dp.Report(
    # sample page
    dp.Group(
        blocks=[
            dp.Plot(bar_chart),
            dp.Plot(donut_chart),
        ], columns=2, )
)

# save and open to visualize output
report.save(path='report.html', open=True)

# upload report
dp.login(token=dp_token)
report.upload(name="Plots", #project='github_dashboard',
              description='Sample plots of most used programming languages.', publicly_visible=True)
