import sys
import webbrowser

from github_api import approve_pull
from github_api import get_pulls
from github_api import merge_pull
from github_api import url_for_pull_request
from os_git import get_current_repo_or_fail
from rubber_stamp_exceptions import RepoNotFoundException
from rubber_stamp_exceptions import PullNotMergeableException


DEFAULT_APPROVE_MESSAGE = ":+1:"


def show_pulls(repo, owner):

    pulls = get_pulls(repo, owner)

    if not pulls:
        return "No open pull requests found."

    string_builder = []

    for pull in pulls:
        number = pull['number']
        title = pull['title']
        author = pull['user']['login']
        string_builder.append("#%s (%s): %s" % (number, author, title))

    return "\n".join(string_builder)


def merge_a_pull(repo, owner, number, merge_method, message):
    if not number:
        return "Must provide pull request number if merging."

    if not message:
        message = ""

    success = False
    try:
        success = merge_pull(repo, owner, number, merge_method, message)
    except PullNotMergeableException:
        return "Pull request #%s in repo %s/%s cannot be merged." % (number, owner, repo)

    if success:
        return "Merged pull request #%s in repo %s/%s." % (number, owner, repo)

    return "Unknown failure merging pull request #%s in repo %s/%s." % (number, owner, repo)


def approve_a_pull(repo, owner, number, message=None):
    if not number:
        return "Must provide pull request number if approving."

    message = message or DEFAULT_APPROVE_MESSAGE
    approve_pull(repo, owner, number, message)
    return "Approved pull request #%s in repo %s/%s." % (number, owner, repo)


def open_pr_in_browser(repo, owner, number):
    if not number:
        return "Must provide a pull request number to open"

    url = url_for_pull_request(repo, owner, number)
    webbrowser.open(url, new=2, autoraise=True)


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    DEFAULT_OWNER = "sproutsocial"

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('verb',
                        choices=['ls', 'merge', 'approve', 'open'], nargs=1)

    try:
        parser.add_argument('-r', '--repo', help='The git repository',
                            default=get_current_repo_or_fail())
    except RepoNotFoundException:
        print "No git repo found. If you aren't in a git repo, specify one."
        sys.exit(1)

    parser.add_argument(
        '-o',
        '--owner',
        help='The GitHub screen name of the owner of the GitHub repository. '
             'Defaults to %s' % DEFAULT_OWNER,
        default=DEFAULT_OWNER
    )

    # TODO this arg does not require option flag
    parser.add_argument('-n', '--number', help="The PR number")
    parser.add_argument('-m', '--message', help="The message to go along with a commit")

    parser.add_argument(
        '-mm',
        '--merge-method',
        help="Method used to merge a pull request.",
        choices=['merge', 'squash', 'rebase'],
        default='squash'
    )

    arguments = parser.parse_args()

    try:
        verb = arguments.verb[0]
        if verb == 'ls':
            res = show_pulls(arguments.repo, arguments.owner)
        elif verb == 'merge':
            res = merge_a_pull(arguments.repo, arguments.owner, arguments.number, arguments.merge_method, arguments.message)
        elif verb == 'approve':
            res = approve_a_pull(arguments.repo, arguments.owner, arguments.number, arguments.message)
        elif verb == 'open':
            res = open_pr_in_browser(arguments.repo, arguments.owner, arguments.number)
        else:
            raise Exception("Should never happen.")
    except Exception as e:
        res = e.message

    print res

if __name__ == "__main__":
    main()
