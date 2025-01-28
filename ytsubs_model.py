import os
import re
import yt_dlp
import requests


# 유튜브 자막추출 모델
class YtSubsModel:
    count = 0

    # 카운터 초기화
    def reset_counter(self):
        self.count = 0

    # 카운터 증가
    def step_counter(self):
        self.count += 1

    # 카운터 값 가져오기
    def get_counter(self):
        return self.count

    # 파일에서 유튜브 동영상 URL 추출
    def extract_video_url(self, file_path):
        # YouTube URL에 맞는 정규식
        youtube_url_pattern = r"https://youtu\.be/[\w-]+|https://www\.youtube\.com/watch\?v=[\w-]+|https://www\.youtube\.com/live/[\w-]+"

        youtube_urls = []

        # 파일 열기
        with open(file_path, "r") as file:
            lines = file.readlines()

            # 각 라인에서 URL 추출
            for line in lines:
                matches = re.findall(youtube_url_pattern, line)
                if matches:
                    youtube_urls.extend(matches)  # URL 리스트에 추가

        return youtube_urls

    # 동영상 URL에서 동영상 정보 추출
    def extract_video_info(self, video_url):
        video_info = None

        try:
            with yt_dlp.YoutubeDL({"quiet": True, "cookiefile": "data/cookie.txt"}) as ydl:
                # 동영상 정보 가져오기
                video_info = ydl.extract_info(video_url, download=False)
        except:
            pass
        
        return video_info

    # 동영상 정보에서 자동생성 자막정보 추출
    def list_automatic_captions(self, video_info):
        # 자동 생성 자막 가져오기
        list_subs_info = video_info.get("automatic_captions", {})
        if not list_subs_info:
            return []
        
        return list_subs_info

    # 자막 다운로드
    def download_caption(self, list_subs_info, list_lang):
        list_subs_vtt = []

        for lang in list_lang:
            # 선택된 언어 자막 다운로드
            formats = list_subs_info[lang]
            vtt_format = next((f for f in formats if f["ext"] == "vtt"), None)

            if not vtt_format: continue

            # URL에서 자막 다운로드
            subtitle_url = vtt_format["url"]

            # 자막URL에서 비디오ID 추출
            vid_temp = subtitle_url.split("?v=")
            if len(vid_temp) < 2: continue

            vid_temp = vid_temp[1].split("&")
            video_id = vid_temp[0]

            # VTT파일 저장경로
            os.makedirs("data/subs", exist_ok=True) # 저장경로 디렉토리 생성
            output_file = os.path.join("data/subs", "{:04d}@".format(self.count) + f"{video_id}.{lang}.vtt")

            # requests로 자막 파일 다운로드
            response = requests.get(subtitle_url)
            if response.status_code == 200:
                with open(output_file, "wb") as file:
                    file.write(response.content)
                list_subs_vtt.append(output_file)
                self.step_counter()
        
        return list_subs_vtt
    

    # 자막 VTT 파일 TXT로 변환
    def vtt_to_txt(self, list_subs_vtt, is_prefix_video_info=False):
        list_subs_txt = []

        for vtt_file in list_subs_vtt:
            with open(vtt_file, 'r', encoding='utf-8') as file:
                vtt_data = file.read()

            # VTT에서 타임코드, 포지션 태그, 메타데이터 제거
            cleaned_text = re.sub(r'WEBVTT.*?(\n\n|\n$)', '', vtt_data, flags=re.DOTALL)  # Remove WEBVTT header and metadata
            cleaned_text = re.sub(r'(\d{2}:\d{2}:\d{2}.\d{3} --> \d{2}:\d{2}:\d{2}.\d{3})|(<.*?>)|align:start position:[^\n]*', '', cleaned_text)

            # 자막 내용만 남기기
            lines = cleaned_text.splitlines()
            processed_lines = []
            seen_lines = set()  # 중복을 제거하기 위한 집합

            for line in lines:
                # 시간 정보 및 빈 줄 제외, 실제 자막 텍스트만 추가
                if not re.match(r'^\d{2}:\d{2}:\d{2}.\d{3}', line) and line.strip() != '':
                    line = line.strip()
                    if line not in seen_lines:  # 중복된 라인은 추가하지 않음
                        seen_lines.add(line)
                        processed_lines.append(line)

            # 텍스트를 하나의 긴 문자열로 변환하고 줄바꿈 제거
            processed_text = " ".join(processed_lines)  # 줄바꿈을 공백으로 바꿔서 하나의 긴 문자열로 결합

            # 비디오 정보 추가
            if is_prefix_video_info:
                # 파일명에서 비디오ID 추출
                vid_temp = vtt_file.split("@")
                vid_temp = vid_temp[1].split(".")
                video_id = vid_temp[0]

                # 비디오 정보 추출
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                video_info = self.extract_video_info(video_url)
                video_title = video_info['title']

            # 텍스트 파일로 저장
            output_txt_file = vtt_file.replace('.vtt', '.txt')
            with open(output_txt_file, 'w', encoding='utf-8') as file:
                if is_prefix_video_info:
                    file.write(f"{video_title}\n")
                    file.write(f"{video_url}\n\n")
                file.write(processed_text)

            # VTT 파일 삭제
            if os.path.exists(vtt_file):
                os.remove(vtt_file)
            
            list_subs_txt.append(output_txt_file)
        
        return list_subs_txt
