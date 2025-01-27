import yt_dlp
import os
import requests
import re
from datetime import datetime

def download_automatic_captions(youtube_url, cookies_file, lang_codes=['en', 'ko']):
    """
    자동 생성 자막(automatic_captions)에서 지정된 언어 자막을 다운로드합니다.
    :param youtube_url: 유튜브 동영상 URL
    :param cookies_file: 쿠키 파일 경로
    :param lang_codes: 다운로드할 언어 코드 리스트 (예: ['en', 'ko'])
    :return: 다운로드된 자막 파일들의 경로 리스트
    """

    # 현재 스크립트 실행 위치를 기준으로 절대 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(script_dir, 'downloads')  # 'downloads' 디렉토리의 절대경로

    os.makedirs(download_dir, exist_ok=True)  # Ensure the downloads directory exists

    downloaded_files = []

    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'cookiefile': cookies_file}) as ydl:
            # 동영상 정보 가져오기
            info_dict = ydl.extract_info(youtube_url, download=False)

            # 자동 생성 자막 가져오기
            automatic_captions = info_dict.get('automatic_captions', {})
            if not automatic_captions:
                print("No automatic captions found for this video.")
                return []

            # 자막 다운로드 조건
            if 'en' in automatic_captions:  # ko 자막이 없고 en 자막이 있으면 en만 다운로드
                lang_to_download = 'en'
            elif 'ko' in automatic_captions:  # ko 자막이 있으면 ko만 다운로드
                lang_to_download = 'ko'
            else:  # ko와 en 자막이 모두 없으면 다운로드하지 않음
                return []

            # 선택된 언어 자막 다운로드
            formats = automatic_captions[lang_to_download]
            vtt_format = next((f for f in formats if f['ext'] == 'vtt'), None)

            if vtt_format:
                # URL에서 자막 다운로드
                subtitle_url = vtt_format['url']

                # 현재 시간을 yyyyMMdd_HHmmss 형식으로 가져오기
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = os.path.join(download_dir, f"{timestamp}.{lang_to_download}.vtt")

                # requests로 자막 파일 다운로드
                response = requests.get(subtitle_url)
                if response.status_code == 200:
                    with open(output_file, 'wb') as file:
                        file.write(response.content)
                    downloaded_files.append(output_file)

    except Exception as e:
        print(f"Error during subtitle download: {e}")

    return downloaded_files


def process_vtt_to_txt(vtt_file, output_txt_file, url=None):
    """
    VTT 파일을 일반 텍스트 파일로 변환하여 시간과 태그를 제거하고 줄바꿈을 없앱니다.
    :param vtt_file: 변환할 VTT 파일 경로
    :param output_txt_file: 저장할 텍스트 파일 경로
    """
    try:
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

        # 텍스트 파일로 저장
        with open(output_txt_file, 'w', encoding='utf-8') as file:
            content = ''
            if url:
                content = url+"\n"
            content += processed_text
            file.write(content)

        # VTT 파일 삭제
        if os.path.exists(vtt_file):
            os.remove(vtt_file)

    except Exception as e:
        print(f"Error during VTT to text conversion: {e}")


# YouTube URL을 추출하는 함수
def extract_youtube_urls(file_path):
    # YouTube URL에 맞는 정규식
    youtube_url_pattern = r"https://youtu\.be/[\w-]+|https://www\.youtube\.com/watch\?v=[\w-]+|https://www\.youtube\.com/live/[\w-]+"

    youtube_urls = []

    # 파일 열기
    with open(file_path, 'r') as file:
        lines = file.readlines()

        # 각 라인에서 URL 추출
        for line in lines:
            matches = re.findall(youtube_url_pattern, line)
            if matches:
                youtube_urls.extend(matches)  # URL 리스트에 추가

    return youtube_urls


# 자막 다운로드 대상 리스트 생성 및 출력 함수
def create_subtitle_download_list(file_path):
    youtube_urls = extract_youtube_urls(file_path)

    cookies_file = 'cookie.txt'  # Replace with your cookie file
    
    # 자막 다운로드 대상 리스트 출력
    if youtube_urls:
        for url in youtube_urls:
            print(url)

            downloaded_files = download_automatic_captions(url, cookies_file)
            if downloaded_files:
                for file in downloaded_files:
                    output_txt_file = file.replace('.vtt', '.txt')
                    process_vtt_to_txt(file, output_txt_file, url=url)

    else:
        print("No YouTube URLs found in the file.")


# Main execution
if __name__ == "__main__":
    create_subtitle_download_list("targets.txt")
