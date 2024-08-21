// use pyo3::prelude::*;
// use pyo3::types::{PyModule, PyAny, PyList};
// use std::path::PathBuf;
// use std::env;
//
// #[tokio::main]
// async fn main() -> PyResult<()> {
//     // TOP_DIR 경로를 가져옴
//     let binding = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
//     let top_dir = binding.parent().unwrap();
//     println!("top_dir: {}", top_dir.display());
//
//     // .env 파일 경로 설정 및 로드
//     let env_path = top_dir.join(".env");
//     dotenv::from_path(env_path).expect(".env file not found");
//     let openai_api_key = env::var("OPENAI_API_KEY").expect("OPENAI_API_KEY not set in .env file");
//     println!("OpenAI API Key: {}", openai_api_key);
//
//     // PYTHONPATH 설정
//     let openai_api_test_path = top_dir.join("openai_api_test");
//     let openai_api_test_service_path = openai_api_test_path.join("service");
//     let openai_api_test_request_path = openai_api_test_service_path.join("request");
//     let openai_api_test_response_path = openai_api_test_service_path.join("response");
//     let openai_api_test_repository_path = openai_api_test_path.join("repository");
//
//     let pythonpath = format!(
//         "{}:{}:{}:{}:{}",
//         openai_api_test_path.display(),
//         openai_api_test_service_path.display(),
//         openai_api_test_request_path.display(),
//         openai_api_test_response_path.display(),
//         openai_api_test_repository_path.display()
//     );
//     env::set_var("PYTHONPATH", &pythonpath);
//
//     // sys.path 업데이트
//     Python::with_gil(|py| {
//         let path = py.import("os")?.getattr("path")?;
//         let abspath = path.call_method1("abspath", ("..",))?;
//
//         let sys = PyModule::import(py, "sys")?;
//         let sys_path: &PyList = sys.getattr("path")?.downcast()?;
//         sys_path.insert(0, abspath)?;
//
//         println!("sys.path after insertion: {:?}", sys_path);
//
//         Ok::<(), PyErr>(())
//     })?;
//
//     // 비동기 작업을 실행하기 위해 Python 코루틴을 Future로 변환
//     let coroutine = Python::with_gil(|py| -> PyResult<Py<PyAny>> {
//         let openai_api_test_service_impl = PyModule::import(py, "openai_api_test.service.openai_api_test_service_impl")
//             .expect("Failed to import module");
//
//         // OpenaiApiTestServiceImpl 클래스 가져오기
//         let service_impl_class = openai_api_test_service_impl.getattr("OpenaiApiTestServiceImpl")?;
//
//         // OpenaiApiTestServiceImpl.getInstance() 호출하여 싱글톤 인스턴스 얻기
//         let service_instance = service_impl_class.call_method0("getInstance")?;
//
//         // letsChat 메서드를 호출하여 코루틴을 반환
//         let coroutine = service_instance.call_method1("letsChat", ("Hello from Rust!",))?;
//         Ok(coroutine.into())
//     })?;
//
//     // 코루틴을 Future로 변환하고 실행하여 Python 객체를 반환
//     let result: PyResult<Py<PyAny>> = Python::with_gil(|py| {
//         let asyncio = py.import("asyncio")?;
//         let result = asyncio.call_method1("run", (coroutine,))?;
//         Ok(result.into())
//     });
//
//     // 결과를 처리하고 출력
//     if let Ok(result) = result {
//         Python::with_gil(|py| -> PyResult<()> {
//             let message: String = result.as_ref(py).get_item("message")?.extract()?;
//             println!("Result from Python: {}", message);
//             Ok(())
//         })?;
//     } else {
//         eprintln!("Failed to execute Python coroutine.");
//     }
//
//     Ok(())
// }

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
    // TOP_DIR 경로를 가져옴
    let binding = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let top_dir = binding.parent().unwrap();
    println!("top_dir: {}", top_dir.display());

    // .env 파일 경로 설정 및 로드
    let env_path = top_dir.join(".env");
    dotenv::from_path(env_path).expect(".env file not found");
    let openai_api_key = env::var("OPENAI_API_KEY").expect("OPENAI_API_KEY not set in .env file");
    println!("OpenAI API Key: {}", openai_api_key);

    // PYTHONPATH 설정
    let openai_api_test_path = top_dir.join("openai_api_test");
    let pythonpath = add_subdirectories_to_pythonpath(&openai_api_test_path);
    env::set_var("PYTHONPATH", &pythonpath);

    // sys.path 업데이트
    Python::with_gil(|py| {
        let path = py.import("os")?.getattr("path")?;
        let abspath = path.call_method1("abspath", ("..",))?;

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
        Python::with_gil(|py| -> PyResult<()> {
            let message: String = result.as_ref(py).get_item("message")?.extract()?;
            println!("Result from Python: {}", message);
            Ok(())
        })?;
    } else {
        eprintln!("Failed to execute Python coroutine.");
    }

    Ok(())
}
