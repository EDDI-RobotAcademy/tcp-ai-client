fn main() {
    println!("cargo:rustc-link-lib=python3.8"); // Python 버전에 따라 수정
    println!("cargo:rustc-link-search=native=/usr/lib/x86_64-linux-gnu"); // Python 라이브러리가 위치한 경로
}
