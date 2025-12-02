from pathlib import Path
import torch, torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import numpy as np, cv2, json

CKPT = Path("models/vision/resnet18/best.pt")
OUT  = Path("reports/explain/vision"); OUT.mkdir(parents=True, exist_ok=True)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = models.resnet18(weights=None)
model.fc = torch.nn.Linear(model.fc.in_features, 2)
sd = torch.load(CKPT, map_location=device)
model.load_state_dict(sd); model.to(device).eval()

target_layer = model.layer4[1].conv2
acts = []
grads = []
def fwd_hook(_, __, output): acts.append(output.detach())
def bwd_hook(_, grad_in, grad_out): grads.append(grad_out[0].detach())
target_layer.register_forward_hook(fwd_hook)
target_layer.register_backward_hook(bwd_hook)

tfm = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
])

def heatmap_for(img_path: Path):
    img = Image.open(img_path).convert("RGB")
    x = tfm(img).unsqueeze(0).to(device)
    logits = model(x)
    cls = logits.argmax(1).item()
    model.zero_grad()
    F.cross_entropy(logits, torch.tensor([cls], device=device)).backward()

    A = acts[-1][0]        # (C,H,W)
    G = grads[-1][0]       # (C,H,W)
    w = G.mean(dim=(1,2))  # (C,)
    cam = (w[:,None,None] * A).sum(0).cpu().numpy()
    cam = np.maximum(cam, 0); cam = (cam - cam.min()) / (cam.max() + 1e-8)

    img_np = np.array(img)[:,:,::-1]  # BGR
    cam_resized = cv2.resize(cam, (img_np.shape[1], img_np.shape[0]))
    heat = (cv2.applyColorMap(np.uint8(255*cam_resized), cv2.COLORMAP_JET)*0.4 + img_np*0.6).astype(np.uint8)
    out_path = OUT/f"gradcam_{img_path.stem}.png"
    cv2.imwrite(str(out_path), heat)
    print("Wrote", out_path)

if __name__ == "__main__":
    sample_dir = Path("data/raw/cv/valid")
    imgs = list(sample_dir.rglob("*.jpg"))[:5] + list(sample_dir.rglob("*.png"))[:5]
    for p in imgs:
        heatmap_for(p)
