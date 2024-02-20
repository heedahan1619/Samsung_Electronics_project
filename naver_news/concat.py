import os
import pandas as pd

# 파일 디렉토리와 기본 파일명 설정
base_filename = "naver_news_202308"
output_filename = "naver_news_20230801_20230831.csv"

# 빈 DataFrame을 생성하여 파일을 순회하면서 데이터를 추가합니다.
combined_df = pd.DataFrame()
for day in range(1, 32):  # 1부터 31까지
    # 파일 경로 생성
    filename = f"{base_filename}{day:02d}.csv"
    if os.path.exists(filename):  # 파일이 존재하는지 확인
        # CSV 파일을 읽어들여 DataFrame에 추가
        df = pd.read_csv(filename)
        combined_df = pd.concat([combined_df, df], ignore_index=True)

# 결과를 하나의 CSV 파일로 저장합니다.
combined_df.to_csv(output_filename, index=False)

# 합친 후 기존 파일 삭제
for day in range(1, 32):
    filename = f"{base_filename}{day:02d}.csv"
    if os.path.exists(filename):
        os.remove(filename)