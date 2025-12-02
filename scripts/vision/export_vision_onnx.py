from pathlib import Path
import yaml
import torch
from torchvision import models


def load_cfg():
    cfg_path = Path("configs/vision/resnet18_classification.yml")
    defaults = {"img_size": 224, "save_dir": "models/vision/resnet18"}
    if cfg_path.exists():
        defaults.update(yaml.safe_load(cfg_path.read_text()) or {})
    return defaults


CFG = load_cfg()
save_dir = Path(CFG["save_dir"])
checkpoint = save_dir / "best.pt"
onnx_path = save_dir / "model.onnx"

if not checkpoint.exists():
    raise SystemExit(f"Checkpoint not found: {checkpoint}")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
state = torch.load(checkpoint, map_location=device)

model = models.resnet18(weights=None)
labels_file = save_dir / "labels.txt"
if not labels_file.exists():
    raise SystemExit(f"Labels file missing: {labels_file}")
classes = labels_file.read_text(encoding="utf-8").splitlines()
num_classes = len(classes) if classes else 1
model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
model.load_state_dict(state)
model.eval().to(device)

dummy = torch.randn(1, 3, int(CFG["img_size"]), int(CFG["img_size"]), device=device)
torch.onnx.export(
    model,
    dummy,
    str(onnx_path),
    input_names=["input"],
    output_names=["logits"],
    dynamic_axes={"input": {0: "batch"}, "logits": {0: "batch"}},
    opset_version=17,
)

print(f"Exported ONNX → {onnx_path}")
