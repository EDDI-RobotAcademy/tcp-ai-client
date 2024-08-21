use pyo3::prelude::*;
use pyo3::types::{PyList, PyModule, PyAny};
use pyo3_asyncio::tokio::into_future;
use std::path::PathBuf;
use std::env;

#[tokio::main]
async fn main() -> PyResult<()> {
    // TOP_DIR 경로를 가져옴
    let binding = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let top_dir = binding.parent().unwrap();
    println!("top_dir: {}", top_dir.display());

    // openai_api_test 디렉토리 경로를 PYTHONPATH에 추가
    let openai_api_test_path = top_dir.join("openai_api_test");
    let openai_api_test_service_path = openai_api_test_path.join("service");

    // PYTHONPATH 설정 - 여러 경로를 콜론(:)으로 구분하여 설정
    let pythonpath = format!(
        "{}:{}",
        openai_api_test_path.display(),
        openai_api_test_service_path.display()
    );
    env::set_var("PYTHONPATH", &pythonpath);

    // Python에서 사용하는 sys.path를 출력하여 경로를 확인
    Python::with_gil(|py| {
        let path = py.import_bound("os")?.getattr("path")?;
        let abspath = path.call_method1("abspath", ("..",))?;

        let sys = PyModule::import_bound(py, "sys")?;
        let sys_path = sys.getattr("path")?.downcast()?;
        sys_path.insert(0, abspath)?;

        // sys.path를 출력하여 경로가 올바르게 추가되었는지 확인
        println!("sys.path after insertion: {:?}", sys_path);

        Ok(())
    })?;

    // 비동기 작업을 실행하기 위해 Python 코루틴을 Future로 변환
    let result = Python::with_gil(|py| -> PyResult<&PyAny> {
        let openai_api_test_service_impl = PyModule::import_bound(py, "openai_api_test.service.openai_api_test_service_impl")
            .expect("Failed to import module");

        // OpenaiApiTestServiceImpl 클래스 가져오기
        let service_impl_class = openai_api_test_service_impl.getattr("OpenaiApiTestServiceImpl")?;

        // OpenaiApiTestServiceImpl.getInstance() 호출하여 싱글톤 인스턴스 얻기
        let service_instance = service_impl_class.call_method0("getInstance")?;

        // letsChat 메서드를 호출하고, 이를 비동기 함수로 변환
        Ok(service_instance.call_method1("letsChat", ("Hello from Rust!",))?.into())
    })?;

    // 코루틴 실행 및 결과 처리
    let result = into_future(result);
    let value: String = result.extract()?;
    println!("Result from Python: {}", value);

    Ok(())
}
