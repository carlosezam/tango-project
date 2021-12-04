import json
import os
from googleapiclient import discovery
from google.oauth2 import service_account


class AndroidPublisher:

    SCOPE = ['https://www.googleapis.com/auth/androidpublisher']

    def __init__(self, package_name, credentials):
        self.package_name = package_name
        self.service = discovery.build('androidpublisher', 'v3', credentials=credentials)

    @classmethod
    def is_file_path(cls, data):
        try:
            return os.path.isfile(data)
        except TypeError:
            return False

    @classmethod
    def get_credentials(cls, info):
        scope = AndroidPublisher.SCOPE

        if cls.is_file_path(info):
            credentials = service_account.Credentials.from_service_account_file(filename=info, scopes=scope)
        else:
            credentials = service_account.Credentials.from_service_account_info(info=info, scopes=scope)

        return credentials

    def insert_edit_id(self):
        request = self.service.edits().insert(packageName=self.package_name)
        response = request.execute()
        return response['id']

    def get_latest_version_code(self, edit_id):
        request = self.service.edits().tracks().list(packageName=self.package_name, editId=edit_id)
        response = request.execute()

        version_codes = [
            v
            for track in response['tracks']
            for release in track['releases']
            if 'versionCodes' in release
            for v in release['versionCodes']
        ]

        return max(version_codes)


def get_punky_publisher():
    account_info = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', './gacs.json')

    if not AndroidPublisher.is_file_path(account_info):
        account_info = json.loads(account_info)

    credentials = AndroidPublisher.get_credentials(account_info)

    return AndroidPublisher('com.carlosezam.punky', credentials)


def main():

    punky = get_punky_publisher()

    edit_id = punky.insert_edit_id()
    version_code = punky.get_latest_version_code(edit_id)

    print("Latest VersionCode:", version_code)


if __name__ == '__main__':
    main()