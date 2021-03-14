#!/usr/bin/python3

from googlesearch import search
import requests
import sys
import subprocess
from bs4 import BeautifulSoup
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit import HTML
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit import print_formatted_text as print
from pygments.lexers import BashLexer

searchText = " ".join(sys.argv[1:])

# Must be Stack Exchange sites
allowedDomains = ["stackoverflow.com", "unix.stackexchange.com", "askubuntu.com", "superuser.com"]


def getResults(query, amount):
    results = []
    for url in search(query + ' linux "Stack Exchange" OR StackOverflow', num=amount, stop=amount):
        # This allows it to appear anywhere in the URL, but that's probably fine
        for domain in allowedDomains:
            if domain in url:
                results.append(url)
                continue
    return results


def fetchCommand(url):
    page = requests.get(url)
    if page.status_code != 200:
        return

    soup = BeautifulSoup(page.text, 'html.parser')

    # Currently unused
    title = soup.find_all('a', {'class': 'question-hyperlink'})

    if len(title) == 0:
        title = 'Unknown title'
    else:
        title = title[0].get_text()

    answers = soup.find_all('div', {'class': 'answer'})

    if len(answers) == 0:
        return

    # Get the first answer on the page (this should be the accepted one, or the one with the most votes)
    answer = answers[0]

    code_blocks = answer.find_all('pre')

    if len(code_blocks) == 0:
        return

    # Get the text in the first code block
    return title, code_blocks[0].get_text().strip()

try:
    print(HTML('<ansigreen><b>Searching...</b></ansigreen>'), end='')

    results = getResults(searchText, 5)

    titles = []
    commands = []
    for result in results:
        result = fetchCommand(result)
        if result is not None:
            title, command = result
            titles.append(title)
            commands.append(command)

    print('\x08' * 12, end='', flush=True)
    print(' ' * 12, end = '')
    print('\x08' * 12, end='', flush=True)

    if len(commands) == 0:
        print(HTML('<ansired><b>No results found.</b></ansired>'))
        sys.exit(1)

    session = PromptSession(history=InMemoryHistory(commands[1:]))
    toRun = session.prompt(
        HTML('<ansiblue><b>&gt;</b></ansiblue> '),
        lexer=PygmentsLexer(BashLexer),
        mouse_support=True,
        default=commands[0])

    subprocess.call(toRun, shell=True)
except KeyboardInterrupt:
    pass
