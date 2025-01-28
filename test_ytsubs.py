import os
import unittest
from ytsubs_model import YtSubsModel

ytsubs = YtSubsModel()


# 유튜브 자막추출 테스트
class YtSubsTestCase(unittest.TestCase):
    # 카운터 설정 및 초기화
    def test_counter(self):
        # 초기화후 10번 증가시키면 카운터 값은 10
        ytsubs.reset_counter()
        for _ in range(0, 10):
            ytsubs.step_counter()
        self.assertEqual(ytsubs.get_counter(), 10)

        # 초기화하면 카운터 값은 0
        ytsubs.reset_counter()
        self.assertEqual(ytsubs.get_counter(), 0)

    # 파일에서 유튜브 동영상 URL 추출
    def test_extract_video_url(self):
        result = ytsubs.extract_video_url("data/test_targets.txt")
        
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)

        # return True

    # 동영상 URL에서 동영상 정보 추출
    def test_extract_video_info(self):
        result = ytsubs.extract_video_url("data/test_targets.txt")
        video_url = result[0]

        video_info = ytsubs.extract_video_info(video_url)

        self.assertIsNotNone(video_info)

    # 동영상 정보에서 자동생성 자막정보 추출
    def test_list_automatic_captions(self):
        list_video_url = ytsubs.extract_video_url("data/test_targets.txt")
        video_url = list_video_url[0]

        video_info = ytsubs.extract_video_info(video_url)
        result = ytsubs.list_automatic_captions(video_info)

        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)

    # 자막 다운로드
    def test_download_caption(self):
        list_video_url = ytsubs.extract_video_url("data/test_targets.txt")
        video_url = list_video_url[0]

        video_info = ytsubs.extract_video_info(video_url)
        list_subs_info = ytsubs.list_automatic_captions(video_info)
        
        result = ytsubs.download_caption(list_subs_info, ['en'])
        
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)

    # 자막 VTT 파일 TXT로 변환
    def test_vtt_to_txt(self):
        list_video_url = ytsubs.extract_video_url("data/test_targets.txt")
        video_url = list_video_url[0]

        video_info = ytsubs.extract_video_info(video_url)
        list_subs_info = ytsubs.list_automatic_captions(video_info)
        
        list_subs_vtt = ytsubs.download_caption(list_subs_info, ['en'])

        result = ytsubs.vtt_to_txt(list_subs_vtt)

        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
