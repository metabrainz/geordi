import os
import sys
import re
import xmltodict
import json

xmltodict.OrderedDict = dict

CI_PARTY_ID_NAMESPACE = "DPID:PADPIDA20090302015"


def process_xml(content):
    try:
        return xmltodict.parse(content,
                               force_cdata=True,
                               attr_prefix='_',
                               cdata_key='text')
    except:
        return None


def entity2json(entity):
    return json.dumps(entity, separators=(',', ':'), sort_keys=True)


def is_list(value):
    return isinstance(value, (list, tuple))


def force_list(node, child_name):
    value = node.get(child_name)
    if value and not is_list(value):
        value = node[child_name] = [value]
    return value


def xml_setup(add_folder, add_data_item, import_manager):
    def _import_ci_xml(xml_file):
        if not xml_file.endswith('.xml'):
            print 'Skipping non-XML file ' + xml_file
            return

        try:
            root = process_xml(open(xml_file, 'r').read())['ern:NewReleaseMessage']
        except Exception as e:
            print 'Skipping %s: %s: %s' % (xml_file, type(e).__name__, e)
            return

        print 'Processing ' + xml_file

        def get_pid(data):
            pid = data['ProprietaryId']

            if is_list(pid):
                raise Exception('Multiple ProprietaryId nodes')

            # I don't see any ProprietaryIds in the dumps that use a namespace
            # other than CI's, but it would probably be bad if there ever were
            # any, so this seems reasonable.
            if pid['_Namespace'] != CI_PARTY_ID_NAMESPACE:
                raise Exception('Missing ProprietaryId')

            return pid['text']

        # A Release is linked to SoundRecordings via their ResourceReferences.
        # In most cases, it appears that the ResourceReference is just the
        # ProprietaryId with the letter 'A' prefixing it, but there are
        # instances where it's not. Also, according to DDEX docs,
        # ResourceReferences are only valid for a specific DdexMessage,
        # meaning we probably shouldn't rely on them for indexing purposes.
        recordings_by_reference = {}

        sound_recordings = root['ResourceList']['SoundRecording']
        if not is_list(sound_recordings):
            sound_recordings = [sound_recordings]

        for recording in sound_recordings:
            recordings_by_reference[recording['ResourceReference']['text']] = recording

            # All the dumps seem to have only one Worldwide territory for all
            # Recordings, so the code assumes that to be a constant and would
            # probably break otherwise.
            details = recording['SoundRecordingDetailsByTerritory']
            if is_list(details):
                raise Exception('Multiple SoundRecordingDetailsByTerritory nodes')

            force_list(details, 'Genre')
            force_list(details, 'ResourceContributor')
            force_list(details, 'IndirectResourceContributor')

            print add_data_item('ci/recording/' + get_pid(recording['SoundRecordingId']), 'recording', entity2json(recording))

        for release in root['ReleaseList']['Release']:
            # Releases of type "TrackRelease" contain a single recording.
            # I'm assuming these are mostly analogous to standalone
            # recordings, because there's a separate "Single" ReleaseType
            # that's also used.
            #
            # So even though we're skipping it here (so that it's not indexed
            # as a release), the recording info for it will have already been
            # indexed above.
            if release['ReleaseType']['text'] == 'TrackRelease':
                continue

            # Handle releases that have only one track.
            resource_references = force_list(release['ReleaseResourceReferenceList'], 'ReleaseResourceReference')

            # Needed by the mapping step to link tracks with recordings.
            for ref in resource_references:
                recording = recordings_by_reference[ref['text']]
                ref['_ProprietaryId'] = get_pid(recording['SoundRecordingId'])
                ref['_RecordingName'] = recording['ReferenceTitle']['TitleText']['text']
                ref['_RecordingDuration'] = recording['Duration']['text']

            # See comment for SoundRecordingDetailsByTerritory above.
            details = release['ReleaseDetailsByTerritory']
            if is_list(details):
                raise Exception('Multiple ReleaseDetailsByTerritory nodes')

            force_list(details, 'Genre')

            print add_data_item('ci/release/' + get_pid(release['ReleaseId']), 'release', entity2json(release))

    @import_manager.command
    def ci(path):
        """Import DDEX data from consolidated independent XML dumps."""
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file_name in files:
                    _import_ci_xml(os.path.join(root, file_name))
        else:
            _import_ci_xml(path)
