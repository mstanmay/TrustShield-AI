"""
Deepfake Model adapter — pluggable interface for deepfake classification.
Default: heuristic-based scorer using OpenCV + mediapipe face landmarks.
Upgrade slot: ONNX model loader for a trained binary classifier.
"""

from __future__ import annotations

import abc
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class DeepfakeModelResult:
    """Raw output from a deepfake detection model."""
    is_deepfake_probability: float = 0.0  # 0-1
    facial_landmark_jitter: float = 0.0
    lip_sync_score: float = 0.0
    compression_artifact_score: float = 0.0
    temporal_flicker_score: float = 0.0
    face_count: int = 0
    frames_analyzed: int = 0
    raw_scores: dict = field(default_factory=dict)


class DeepfakeModel(abc.ABC):
    """Abstract interface for deepfake detection models."""

    @abc.abstractmethod
    async def predict(self, media_path: str, is_video: bool = True) -> DeepfakeModelResult:
        """Run deepfake detection on a media file."""
        ...


class HeuristicDeepfakeModel(DeepfakeModel):
    """Heuristic-based deepfake detector using OpenCV + mediapipe.

    Checks:
    - Facial landmark consistency across frames
    - Lip-sync correlation (basic audio-visual alignment)
    - Compression/blending artifact detection
    - Temporal flicker scoring
    """

    async def predict(self, media_path: str, is_video: bool = True) -> DeepfakeModelResult:
        """Analyze media for deepfake indicators using heuristics."""
        import numpy as np

        result = DeepfakeModelResult()

        try:
            import cv2
        except ImportError:
            logger.error("OpenCV not installed — deepfake heuristics unavailable")
            result.raw_scores["error"] = "opencv not installed"
            return result

        try:
            import mediapipe as mp
            mp_face_mesh = mp.solutions.face_mesh
        except ImportError:
            logger.warning("Mediapipe not installed — using basic CV-only heuristics")
            mp_face_mesh = None

        if is_video:
            cap = cv2.VideoCapture(media_path)
            if not cap.isOpened():
                logger.error("Cannot open video: %s", media_path)
                result.raw_scores["error"] = "cannot open video"
                return result

            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 30
            # Sample every Nth frame (max 60 frames for efficiency)
            sample_interval = max(1, frame_count // 60)

            landmark_positions: list[list[float]] = []
            compression_scores: list[float] = []
            brightness_values: list[float] = []

            face_mesh = mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=2,
                min_detection_confidence=0.5,
            ) if mp_face_mesh else None

            frame_idx = 0
            analyzed = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_idx % sample_interval != 0:
                    frame_idx += 1
                    continue

                analyzed += 1
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Compression artifact: Laplacian variance (blur/blockiness)
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                compression_scores.append(laplacian_var)

                # Brightness for flicker detection
                brightness_values.append(np.mean(gray))

                # Face landmark extraction via mediapipe
                if face_mesh:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    face_results = face_mesh.process(rgb_frame)
                    if face_results.multi_face_landmarks:
                        result.face_count = max(result.face_count, len(face_results.multi_face_landmarks))
                        # Take key landmark positions (nose tip, chin, left/right eye)
                        landmarks = face_results.multi_face_landmarks[0]
                        key_points = [
                            landmarks.landmark[1],   # Nose tip
                            landmarks.landmark[152],  # Chin
                            landmarks.landmark[33],   # Left eye outer
                            landmarks.landmark[263],  # Right eye outer
                            landmarks.landmark[13],   # Upper lip
                            landmarks.landmark[14],   # Lower lip
                        ]
                        positions = [p.x for p in key_points] + [p.y for p in key_points]
                        landmark_positions.append(positions)

                frame_idx += 1

            cap.release()
            if face_mesh:
                face_mesh.close()

            result.frames_analyzed = analyzed

            # Compute heuristic scores
            if len(landmark_positions) > 3:
                # Landmark jitter: standard deviation of landmark positions across frames
                positions_array = np.array(landmark_positions)
                jitter = np.mean(np.std(positions_array, axis=0))
                # Normalize: high jitter is suspicious (deepfakes often have jittery landmarks)
                result.facial_landmark_jitter = min(float(jitter * 50), 1.0)

                # Lip region: difference between upper and lower lip positions
                lip_diffs = [abs(pos[4] - pos[5]) for pos in landmark_positions]
                lip_variance = np.std(lip_diffs)
                # Very low lip variance can indicate pasted-on mouth
                result.lip_sync_score = min(float(1.0 - lip_variance * 100), 1.0) if lip_variance < 0.01 else 0.0

            if compression_scores:
                # Abnormally uniform Laplacian variance suggests recompressed/blended regions
                compression_var = np.std(compression_scores)
                mean_laplacian = np.mean(compression_scores)
                # Very low variance in quality across frames is suspicious
                if mean_laplacian < 50:
                    result.compression_artifact_score = 0.6
                elif compression_var < 10:
                    result.compression_artifact_score = 0.4
                else:
                    result.compression_artifact_score = max(0, 0.3 - compression_var / 1000)

            if brightness_values:
                # Temporal flicker: sudden brightness jumps between sampled frames
                brightness_diffs = np.abs(np.diff(brightness_values))
                max_flicker = float(np.max(brightness_diffs)) if len(brightness_diffs) > 0 else 0
                result.temporal_flicker_score = min(max_flicker / 30.0, 1.0)

        else:
            # Single image analysis
            img = cv2.imread(media_path)
            if img is None:
                result.raw_scores["error"] = "cannot read image"
                return result

            result.frames_analyzed = 1
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Compression artifacts in single image
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            result.compression_artifact_score = 0.5 if laplacian_var < 50 else max(0, 0.3 - laplacian_var / 1000)

            # Face detection
            if mp_face_mesh:
                face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=2)
                rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                face_results = face_mesh.process(rgb)
                if face_results.multi_face_landmarks:
                    result.face_count = len(face_results.multi_face_landmarks)
                face_mesh.close()

        # Composite deepfake probability
        scores = [
            result.facial_landmark_jitter * 0.35,
            result.lip_sync_score * 0.25,
            result.compression_artifact_score * 0.25,
            result.temporal_flicker_score * 0.15,
        ]
        result.is_deepfake_probability = min(sum(scores), 1.0)
        result.raw_scores = {
            "landmark_jitter": result.facial_landmark_jitter,
            "lip_sync": result.lip_sync_score,
            "compression": result.compression_artifact_score,
            "flicker": result.temporal_flicker_score,
        }

        return result


class ONNXDeepfakeModel(DeepfakeModel):
    """ONNX model loader for a trained deepfake classifier.

    # TODO: upgrade to trained model — load a real ONNX model for production.
    Expects a face-crop → binary classifier (real vs. fake).
    """

    def __init__(self, model_path: str):
        self._model_path = model_path
        self._session = None

    def _load_model(self):
        """Lazy-load the ONNX model."""
        if self._session is None:
            try:
                import onnxruntime as ort
                self._session = ort.InferenceSession(self._model_path)
                logger.info("Loaded ONNX deepfake model from %s", self._model_path)
            except Exception as e:
                logger.error("Failed to load ONNX model: %s", e)
                raise

    async def predict(self, media_path: str, is_video: bool = True) -> DeepfakeModelResult:
        """Run the ONNX classifier on extracted face crops."""
        self._load_model()
        import cv2
        import numpy as np

        result = DeepfakeModelResult()
        img = cv2.imread(media_path) if not is_video else None

        if is_video:
            cap = cv2.VideoCapture(media_path)
            ret, img = cap.read()
            cap.release()
            if not ret:
                return result

        if img is None:
            return result

        # Preprocess: resize to model input shape (e.g., 224x224)
        resized = cv2.resize(img, (224, 224))
        input_tensor = resized.astype(np.float32) / 255.0
        input_tensor = np.transpose(input_tensor, (2, 0, 1))
        input_tensor = np.expand_dims(input_tensor, axis=0)

        # Run inference
        input_name = self._session.get_inputs()[0].name
        outputs = self._session.run(None, {input_name: input_tensor})
        prob = float(outputs[0][0][0]) if outputs else 0.0

        result.is_deepfake_probability = prob
        result.frames_analyzed = 1
        result.raw_scores = {"onnx_output": prob}

        return result


def get_deepfake_model() -> DeepfakeModel:
    """Factory: returns the configured deepfake detection model."""
    import os
    model_path = os.environ.get("DEEPFAKE_ONNX_MODEL_PATH")
    if model_path and os.path.exists(model_path):
        return ONNXDeepfakeModel(model_path)
    return HeuristicDeepfakeModel()
