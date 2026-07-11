import os

# 1) 파일을 생성할 대상 디렉토리 (현재 폴더 기준 ./test)
target_dir = "test"

# 2) 디렉토리가 없으면 만든다. exist_ok=True 이므로 이미 있어도 에러 안 남.
os.makedirs(target_dir, exist_ok=True)

# 3) 생성할 파일의 전체 경로 (OS에 맞게 경로 구분자를 붙여줌)
file_path = os.path.join(target_dir, "hello_linux.txt")

# 4) 파일을 쓰기 모드("w")로 열어 문자열을 기록한다.
#    with 문을 쓰면 블록이 끝날 때 파일이 자동으로 닫힌다(close).
with open(file_path, "w") as f:
    f.write("Hello Linux\n")

# 5) 결과 안내
print(f"'{file_path}' 파일을 생성했습니다.")
