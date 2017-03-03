import os

import utils.process_utils as process_utils
import utils.xml_utils as xml_utils


def get_local_changed_files(abs_path, ignore_unversioned=True):
    status_info = process_utils.invoke(['svn', 'status', '--xml', abs_path])

    entries_xpath = '*/entry'
    found_results = xml_utils.find_in_string(status_info, [entries_xpath])
    entries = found_results[entries_xpath]

    return svn_xml_status_to_files(entries, ignore_unversioned)


def svn_status_to_files(all_lines):
    result = []

    for line in all_lines:
        if os.name != 'nt':
            if not ('/' in line):
                continue
            file_path = line[line.index("/"):]

        else:
            if not ('\\' in line):
                continue
            file_path = line[line.index(':\\') - 1:]

        result.append(file_path)

    return result


def svn_xml_status_to_files(found_entries, ignore_unversioned=True):
    result = []

    for entry in found_entries:
        status_info = entry['wc-status']
        status = status_info['item']

        if ignore_unversioned and (status == 'unversioned'):
            continue

        path = entry['path']
        result.append(path)

    return result


def get_revision_changed_files(abs_path, from_revision, to_revision):
    changed_files = process_utils.invoke(
        ['svn', 'diff', '--summarize', '-r' + from_revision + ':' + to_revision, abs_path])
    lines = changed_files.split('\n')

    return svn_status_to_files(lines)


def get_revision(project_path):
    svn_info = process_utils.invoke(['svn', 'info', project_path])
    info_lines = svn_info.split('\n')

    revision_prefix = 'Revision: '

    for line in info_lines:
        if line.startswith(revision_prefix):
            return line[len(revision_prefix):]

    raise Exception("Couldn't get svn revision in " + project_path)
