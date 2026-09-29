from fastapi import APIRouter, File, HTTPException, UploadFile

try:
    from backend.app.schemas.analysis import AnalysisRequest
    from backend.app.services.analysis_service import AnalysisService
    from backend.app.services.text_extraction import extract_text, validate_file
except ModuleNotFoundError:  # pragma: no cover - compatibility when run from backend package path
    from app.schemas.analysis import AnalysisRequest
    from app.services.analysis_service import AnalysisService
    from app.services.text_extraction import extract_text, validate_file

router = APIRouter()
service = AnalysisService()


@router.post('/api/analyze')
def analyze_text(payload: AnalysisRequest):
    try:
        result = service.analyze_text(payload.text)
        return {'success': True, 'data': result}
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=500, detail={'success': False, 'error': {'code': 'AI_ERROR', 'message': str(exc)}})


@router.post('/api/analyze/file')
async def analyze_file(file: UploadFile = File(...)):
    try:
        validate_file(file.filename, file.size)
        content = await file.read()
        temp_path = f'/tmp/{file.filename}'
        with open(temp_path, 'wb') as handle:
            handle.write(content)
        extracted_text = extract_text(temp_path)
        if not extracted_text.strip():
            raise ValueError('The uploaded file does not contain any readable text.')
        result = service.analyze_text(extracted_text)
        return {'success': True, 'data': result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={'success': False, 'error': {'code': 'INVALID_FILE', 'message': str(exc)}})
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=500, detail={'success': False, 'error': {'code': 'AI_ERROR', 'message': str(exc)}})
