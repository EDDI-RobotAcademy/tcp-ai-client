use pyo3::prelude::*;
use pyo3::types::{PyModule, PyAny, PyList};
use std::path::{Path, PathBuf};
use std::{env, fs};

fn add_subdirectories_to_pythonpath(root_path: &Path) -> String {
    let mut paths = vec![root_path.to_path_buf()];  // 루트 디렉토리 추가

    if let Ok(entries) = fs::read_dir(root_path) {
        for entry in entries.filter_map(Result::ok) {
            let path = entry.path();
            if path.is_dir() {
                paths.push(path.clone());
                let sub_paths = add_subdirectories_to_pythonpath(&path);  // 재귀적으로 하위 디렉토리 탐색
                paths.push(PathBuf::from(sub_paths));
            }
        }
    }

    // 경로를 콜론(:)으로 구분하여 하나의 문자열로 연결
    paths.iter().map(|p| p.display().to_string()).collect::<Vec<String>>().join(":")
}

#[tokio::main]
async fn main() -> PyResult<()> {
    match env::current_dir() {
        Ok(path) => println!("현재 작업 디렉토리: {}", path.display()),
        Err(e) => println!("현재 작업 디렉토리 획득 실패: {}", e),
    }

    match env::current_exe() {
        Ok(path) => println!("현재 구동 디렉토리: {}", path.display()),
        Err(e) => println!("현재 구동 디렉토리 획득 실패: {}", e),
    }

    let argumentList: Vec<String> = env::args().collect();
    println!("Received argumentList: {:?}", argumentList);

    if argumentList.len() < 3 {
        println!("사용 방법이 잘못 되었습니다!")
    }

    let packageName = &argumentList[1];
    let functionName = &argumentList[2];
    let parameterList = &argumentList[3];
    println!("packageName: {}", packageName);
    println!("functionName: {}", functionName);
    println!("parameterList: {}", parameterList);

    // TOP_DIR 경로를 가져옴
    let binding = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let top_dir = binding.parent().unwrap();
    println!("top_dir: {}", top_dir.display());

    // .env 파일 경로 설정 및 로드
    let env_path = top_dir.join(".env");
    dotenv::from_path(env_path).expect(".env file not found");
    let openai_api_key = env::var("OPENAI_API_KEY").expect("OPENAI_API_KEY not set in .env file");

    // PYTHONPATH 설정
    let openai_api_test_path = top_dir.join("openai_api_test");
    println!("openai_api_test_path: {}", openai_api_test_path.display());

    let pythonpath = add_subdirectories_to_pythonpath(&openai_api_test_path);
    println!("pythonpath: {}", pythonpath);
    env::set_var("PYTHONPATH", &pythonpath);

    // sys.path 업데이트
    Python::with_gil(|py| {
        let path = py.import("os")?.getattr("path")?;
        // TODO: 홀로 실행하냐 연동해서 실행하냐에 따라 자동으로 분류되게 만들어야함 (일단 그냥 감)
        // let abspath = path.call_method1("abspath", ("..",))?;
        let abspath = path.call_method1("abspath", ("",))?;

        let sys = PyModule::import(py, "sys")?;
        let sys_path: &PyList = sys.getattr("path")?.downcast()?;
        sys_path.insert(0, abspath)?;

        println!("sys.path after insertion: {:?}", sys_path);

        Ok::<(), PyErr>(())
    })?;

    // 비동기 작업을 실행하기 위해 Python 코루틴을 Future로 변환
    let coroutine = Python::with_gil(|py| -> PyResult<Py<PyAny>> {
        let openai_api_test_service_impl = PyModule::import(py, "openai_api_test.service.openai_api_test_service_impl")
            .expect("Failed to import module");

        // OpenaiApiTestServiceImpl 클래스 가져오기
        let service_impl_class = openai_api_test_service_impl.getattr("OpenaiApiTestServiceImpl")?;

        // OpenaiApiTestServiceImpl.getInstance() 호출하여 싱글톤 인스턴스 얻기
        let service_instance = service_impl_class.call_method0("getInstance")?;

        // letsChat 메서드를 호출하여 코루틴을 반환
        let coroutine = service_instance.call_method1("letsChat", ("Hello from Rust!",))?;
        Ok(coroutine.into())
    })?;

    // 코루틴을 Future로 변환하고 실행하여 Python 객체를 반환
    let result: PyResult<Py<PyAny>> = Python::with_gil(|py| {
        let asyncio = py.import("asyncio")?;
        let result = asyncio.call_method1("run", (coroutine,))?;
        Ok(result.into())
    });

    // 결과를 처리하고 출력
    if let Ok(result) = result {
        let message = Python::with_gil(|py| -> PyResult<String> {
            let message: String = result.as_ref(py).get_item("message")?.extract()?;
            println!("Result from Python: {}", message);
            Ok(message)
        })?;

        Ok(message)
    } else {
        eprintln!("Failed to execute Python coroutine.");
        Ok("python coroutine 실행 실패!".to_string())
    }

    Ok(())
}
