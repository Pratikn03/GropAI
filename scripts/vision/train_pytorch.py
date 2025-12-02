from pathlib import Path
import time
import yaml
from typing import Dict
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader


def load_config() -> Dict:
    cfg_path = Path("configs/vision/resnet18_classification.yml")
    defaults = {
        "train_dir": "data/raw/cv/train",
        "val_dir": "data/raw/cv/valid",
        "epochs": 10,
        "batch_size": 32,
        "img_size": 224,
        "lr": 1e-3,
        "patience": 3,
        "num_workers": 4,
        "save_dir": "models/vision/resnet18"
    }
    if cfg_path.exists():
        overrides = yaml.safe_load(cfg_path.read_text()) or {}
        defaults.update(overrides)
    return defaults


CFG = load_config()
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

train_transforms = transforms.Compose([
    transforms.RandomResizedCrop(int(CFG["img_size"])),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

val_transforms = transforms.Compose([
    transforms.Resize(int(CFG["img_size"] * 1.1)),
    transforms.CenterCrop(int(CFG["img_size"])),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

train_path = Path(CFG["train_dir"])
val_path = Path(CFG["val_dir"])
if not train_path.exists():
    raise SystemExit(f"Training folder not found: {train_path}")

train_dataset = datasets.ImageFolder(train_path, transform=train_transforms)
val_dataset = datasets.ImageFolder(val_path, transform=val_transforms) if val_path.exists() else None
if len(train_dataset.classes) == 0:
    raise SystemExit("No classes found under training directory.")

train_loader = DataLoader(
    train_dataset, batch_size=int(CFG["batch_size"]), shuffle=True,
    num_workers=int(CFG["num_workers"]), pin_memory=True
)
val_loader = (
    DataLoader(val_dataset, batch_size=int(CFG["batch_size"]), shuffle=False,
               num_workers=int(CFG["num_workers"]), pin_memory=True)
    if val_dataset else None
)

model = models.resnet18(weights=None)
model.fc = nn.Linear(model.fc.in_features, len(train_dataset.classes))
model = model.to(DEVICE)

optimizer = optim.Adam(model.parameters(), lr=float(CFG["lr"]))
criterion = nn.CrossEntropyLoss()

save_dir = Path(CFG["save_dir"])
save_dir.mkdir(parents=True, exist_ok=True)
save_dir.joinpath("labels.txt").write_text("\n".join(train_dataset.classes), encoding="utf-8")

best_acc = 0.0
epochs_without_improve = 0

for epoch in range(1, int(CFG["epochs"]) + 1):
    model.train()
    running_loss = 0.0
    total = 0
    correct = 0
    for X, y in train_loader:
        X, y = X.to(DEVICE), y.to(DEVICE)
        optimizer.zero_grad()
        logits = model(X)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * X.size(0)
        preds = logits.argmax(dim=1)
        correct += (preds == y).sum().item()
        total += X.size(0)

    train_acc = correct / total if total else 0.0
    train_loss = running_loss / total if total else 0.0

    val_acc = 0.0
    if val_loader:
        model.eval()
        val_total = 0
        val_correct = 0
        with torch.no_grad():
            for X, y in val_loader:
                X, y = X.to(DEVICE), y.to(DEVICE)
                logits = model(X)
                preds = logits.argmax(dim=1)
                val_correct += (preds == y).sum().item()
                val_total += X.size(0)
        val_acc = val_correct / val_total if val_total else 0.0

    monitor_acc = val_acc if val_loader else train_acc
    print(
        f"Epoch {epoch} | loss={train_loss:.4f} | train_acc={train_acc:.4f} | val_acc={val_acc:.4f}"
    )

    if monitor_acc > best_acc:
        best_acc = monitor_acc
        epochs_without_improve = 0
        torch.save(model.state_dict(), save_dir / "best.pt")
        print("Saved best checkpoint.")
    else:
        epochs_without_improve += 1
    if epochs_without_improve >= int(CFG["patience"]):
        print("Early stopping triggered.")
        break

metrics_dir = Path("reports/metrics")
metrics_dir.mkdir(parents=True, exist_ok=True)
runs_path = metrics_dir / "runs.csv"
if not runs_path.exists():
    runs_path.write_text("run_id,task,model,fold,metric_name,metric_value,split,ts\n", encoding="utf-8")
with runs_path.open("a", encoding="utf-8") as fh:
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    fh.write(f"{int(time.time())},vision,resnet18,best,accuracy,{best_acc:.4f},val,{ts}\n")

print(f"Training complete. Best accuracy: {best_acc:.4f}")
print(f"Artifacts written to {save_dir}")
