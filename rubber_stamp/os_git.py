import os
from subprocess import call
from subprocess import check_output
from subprocess import CalledProcessError
from tempfile import NamedTemporaryFile

from rubber_stamp_exceptions import RepoNotFoundException


def get_current_repo_or_fail():
    """
    Gets the name of the git repo that houses the current working directory.

    Throws Exception if not a git repo or call fails.
    """
    cmd = ['git', 'rev-parse', '--show-toplevel']
    try:
        with open(os.devnull, 'w') as devnull:
            full_path = check_output(cmd, stderr=devnull)
    except CalledProcessError:
        raise RepoNotFoundException

    return os.path.basename(full_path).strip()


def get_message_from_editor():
    """
    Opens a user's editor and returns the contents of the file that they create.
    """
    editor = os.environ.get('EDITOR','vim')

    initial_message = "# Enter your message here.  Any line beginning with '#' will be ignored.\n\n"

    with NamedTemporaryFile(suffix=".tmp") as tf:
        tf.write(initial_message)
        tf.flush()
        call([editor, tf.name])

        with open(tf.name, 'r') as tfo:
            message = tfo.read()

    return '\n'.join(line for line in message.split('\n') if not line.startswith('#'))


if __name__ == "__main__":
    m = get_message_from_editor()
    print m
