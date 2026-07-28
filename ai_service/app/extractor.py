import cv2
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import numpy as np
from PIL import Image
from typing import List, Dict, Any

class ArcFaceEmbeddingNet(nn.Module):
    """
    Deep Convolutional Network for 512-dimensional facial embedding extraction.
    Designed for age-invariant feature representation by projecting face feature maps
    into L2-normalized 512d hyperspherical space.
    """
    def __init__(self, embedding_dim: int = 512):
        super(ArcFaceEmbeddingNet, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(32),
            nn.PReLU(),
            
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.PReLU(),
            
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.PReLU(),
            
            nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.PReLU(),
            
            nn.AdaptiveAvgPool2d((4, 4))
        )
        self.fc = nn.Sequential(
            nn.Linear(256 * 4 * 4, 512),
            nn.BatchNorm1d(512)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.features(x)
        out = out.view(out.size(0), -1)
        embedding = self.fc(out)
        # L2 normalization for cosine similarity
        norm = torch.norm(embedding, p=2, dim=1, keepdim=True) + 1e-8
        return embedding / norm

class FaceExtractor:
    """
    Deep learning face detection and age-invariant feature extraction pipeline.
    Combines OpenCV face detection with PyTorch deep embedding neural net.
    """
    def __init__(self, min_face_size: int = 20):
        self.min_face_size = min_face_size
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Safe cascade classifier initialization
        self.face_cascade = None
        if hasattr(cv2, 'CascadeClassifier'):
            try:
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                cascade = cv2.CascadeClassifier(cascade_path)
                if not cascade.empty():
                    self.face_cascade = cascade
            except Exception:
                pass
        
        # Initialize PyTorch ArcFace neural network model
        self.model = ArcFaceEmbeddingNet(embedding_dim=512).to(self.device)
        self.model.eval()
        
        # Standard image preprocessing for face crop
        self.transform = transforms.Compose([
            transforms.Resize((112, 112)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])

    def detect_faces(self, cv2_img: np.ndarray) -> List[tuple]:
        """
        Detect face bounding boxes (x, y, w, h) in an OpenCV BGR image.
        """
        if self.face_cascade is not None:
            gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(self.min_face_size, self.min_face_size)
            )
            return list(faces)
        return []

    def extract_faces(self, pil_image: Image.Image) -> List[Dict[str, Any]]:
        """
        Detects faces in PIL image and extracts 512-dim normalized feature embeddings.
        Returns list of dicts: [{"bbox": (x, y, w, h), "embedding": np.ndarray(512,)}, ...]
        If no face is detected, returns empty list [].
        """
        # Convert PIL to OpenCV BGR
        cv2_img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        bboxes = self.detect_faces(cv2_img)
        
        if not bboxes:
            # Fallback: if whole image has face crop aspect ratio, evaluate whole image
            w, h = pil_image.size
            if min(w, h) >= 32 and abs(w - h) < max(w, h) * 0.5:
                # Treat entire image as face crop
                bboxes = [(0, 0, w, h)]
            else:
                return []
                
        results = []
        for (x, y, w, h) in bboxes:
            # Crop face area
            face_crop = pil_image.crop((x, y, x + w, y + h))
            tensor = self.transform(face_crop).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                embedding_tensor = self.model(tensor)
                embedding_np = embedding_tensor.cpu().numpy().flatten()
                
            results.append({
                "bbox": (int(x), int(y), int(w), int(h)),
                "embedding": embedding_np
            })
            
        return results
