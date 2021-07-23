class YoutubeEmail(object):
    def __init__(self, from_email_: str, subject_: str, youtube_links_: list, msg_index_: int):
        self.from_email = from_email_
        self.subject = subject_
        self.youtube_links = youtube_links_
        self.msg_index = msg_index_
        # print(self)

    def __str__(self):
        res = "Email: \n "
        res += f"From:          {self.from_email}\n"
        res += f"Subject:       {self.subject}\n"
        res += f"Msg-Index:     {self.msg_index}\n"
        res += f"Youtube Links: {self.youtube_links}\n"
        return res
