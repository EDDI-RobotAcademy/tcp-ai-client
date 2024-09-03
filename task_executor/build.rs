use std::env;
use std::process::Command;
use std::path::Path;

fn main() {
    // 운영 체제를 감지
    let target_os = env::var("CARGO_CFG_TARGET_OS").unwrap();

    match target_os.as_str() {
        "linux" => {
            // 리눅스 설정
            println!("cargo:rustc-link-lib=python3.8"); // 리눅스의 Python 버전에 따라 수정
            println!("cargo:rustc-link-search=native=/usr/lib/x86_64-linux-gnu"); // 리눅스에서 Python 라이브러리 위치 경로
        },
        "macos" => {
            // MacOS 설정
            let python_lib_dir = env::var("LIBRARY_PATH").expect("LIBRARY_PATH must be set to Python lib directory");
            println!("cargo:rustc-link-search=native={}", python_lib_dir);

            // Python 3.x 버전을 찾도록 설정
            println!("cargo:rustc-link-lib=python3.10");
            if let Ok(python_path) = env::var("PYTHON3") {
                println!("cargo:rerun-if-env-changed=PYTHON3");
                println!("cargo:rustc-env=PYTHON3={}", python_path);
            } else if let Ok(python_path) = env::var("PYTHON_HOME") {
                println!("cargo:rerun-if-env-changed=PYTHON_HOME");
                println!("cargo:rustc-env=PYTHON_HOME={}", python_path);
            }

            // MacOS M1/M2 환경에서 ARM 아키텍처 지원
            println!("cargo:rerun-if-env-changed=PYO3_PYTHON");
        },
        _ => {
        }
    }
}
