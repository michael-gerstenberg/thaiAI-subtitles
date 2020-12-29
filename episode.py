#db = connect_mongo_db()
#from episode import Episode
from pathlib import Path
import re

class Episode:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.errors = []
        self.season = None
        self.episode = None
        self.word_list = {}
        self.language = None
        self.file_type = Path(self.file_path).suffix.replace('.')
        self.content = None
        self.content_parsed = None

        self.scrape_season_and_episode_from_file_path()
        self.scrape_language_from_file_path()
        self.scrape_content()

    def scrape_season_and_episode_from_file_path(self):
        success = False
        file_name = Path(self.file_path).name.split('.')
        for part in file_name:
            if len(part) == 6 and part[0] == "S":
                self.season = int(part[1:3])
                self.episode = int(part[4:6])
                success = True
        if success == False:
            self.errors.append("Can't find season and episode number.")

    def scrape_language_from_file_path(self):
        self.language = self.file_path.split('.')[-1].replace('[cc]', '')


    def scrape_content(self):
        if self.file_type == 'vtt':
            self.scrape_vtt_content()
        if self.file_type == 'dfxp':
            self.scrape_dfxp_content()
        else:
            self.errors.append("Unsupported filetype.")
    
    def scrape_vtt_content(self):
        return True

    def scrape_dfxp_content(self):
        return True



    def replace_nonchar(self, s: str):
        s = re.sub("[\(\[].*?[\)\]]", "", s)
        rx = re.compile('([&#])')
        s = rx.sub(r'\\\1', s)
        forbidden_characters = ['-  ', '- ', '...', '?', '!', '-', '.', '"', "'", 'ฯ', '[', ']', ',']
        s = re.sub(r'[0-9]', '', s)
        return s.strip()