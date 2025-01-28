from ytsubs_model import YtSubsModel

ytsubs = YtSubsModel()

if __name__ == "__main__":
    ytsubs.reset_counter()
    list_video_url = ytsubs.extract_video_url("data/prod_targets.txt")

    for video_url in list_video_url:
        video_info = ytsubs.extract_video_info(video_url)
        if not video_info: continue

        list_subs_info = ytsubs.list_automatic_captions(video_info)
        if len(list_subs_info) == 0: continue
        
        list_subs_vtt = ytsubs.download_caption(list_subs_info, ['en'])
        if len(list_subs_info) == 0: continue

        ytsubs.vtt_to_txt(list_subs_vtt, is_prefix_video_info=True)
