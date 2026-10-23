#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from openwakeword.train import Model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a small local Galileo openWakeWord pilot model.")
    parser.add_argument("feature_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--epochs", type=int, default=200)
    parser.add_argument("--learning-rate", type=float, default=0.0005)
    parser.add_argument("--layer-size", type=int, default=128)
    parser.add_argument("--seed", type=int, default=87)
    return parser.parse_args()


def load_features(feature_dir: Path, split: str) -> tuple[np.ndarray, np.ndarray]:
    positive = np.load(feature_dir / f"positive_features_{split}.npy")
    negative = np.load(feature_dir / f"negative_features_{split}.npy")
    x = np.vstack([positive, negative]).astype(np.float32)
    y = np.hstack([np.ones(len(positive)), np.zeros(len(negative))]).astype(np.float32)
    return x, y


def metrics(predictions: torch.Tensor, labels: torch.Tensor) -> dict[str, float]:
    predicted_labels = (predictions >= 0.5).float()
    correct = (predicted_labels == labels).float().mean().item()
    positives = labels == 1
    negatives = labels == 0
    recall = (predicted_labels[positives] == 1).float().mean().item() if positives.any() else 0.0
    false_positive_rate = (predicted_labels[negatives] == 1).float().mean().item() if negatives.any() else 0.0
    return {
        "accuracy": correct,
        "recall": recall,
        "false_positive_rate": false_positive_rate,
    }


def main() -> int:
    args = parse_args()
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    x_train, y_train = load_features(args.feature_dir, "train")
    x_test, y_test = load_features(args.feature_dir, "test")
    input_shape = tuple(x_train.shape[1:])

    model = Model(n_classes=1, input_shape=input_shape, model_type="dnn", layer_dim=args.layer_size)
    net = model.model.to(model.device)
    optimizer = torch.optim.Adam(net.parameters(), lr=args.learning_rate)
    loss_fn = torch.nn.BCELoss()

    x_train_t = torch.from_numpy(x_train).to(model.device)
    y_train_t = torch.from_numpy(y_train[:, None]).to(model.device)
    x_test_t = torch.from_numpy(x_test).to(model.device)
    y_test_t = torch.from_numpy(y_test[:, None]).to(model.device)

    history = []
    for epoch in range(1, args.epochs + 1):
        order = torch.randperm(x_train_t.shape[0], device=model.device)
        optimizer.zero_grad()
        predictions = net(x_train_t[order])
        loss = loss_fn(predictions, y_train_t[order])
        loss.backward()
        optimizer.step()

        if epoch == 1 or epoch % 10 == 0 or epoch == args.epochs:
            with torch.no_grad():
                train_predictions = net(x_train_t)
                test_predictions = net(x_test_t)
            history.append(
                {
                    "epoch": epoch,
                    "loss": float(loss.detach().cpu()),
                    "train": metrics(train_predictions.cpu(), y_train_t.cpu()),
                    "test": metrics(test_predictions.cpu(), y_test_t.cpu()),
                }
            )

    model_path = args.output_dir / "galileo_pilot_state.pt"
    torch.save(
        {
            "state_dict": net.cpu().state_dict(),
            "input_shape": input_shape,
            "model_type": "dnn",
            "layer_size": args.layer_size,
        },
        model_path,
    )
    net.eval()
    onnx_path = args.output_dir / "galileo_pilot.onnx"
    torch.onnx.export(
        net,
        torch.zeros((1,) + input_shape, dtype=torch.float32),
        onnx_path,
        input_names=["input"],
        output_names=["galileo"],
        opset_version=18,
    )

    report = {
        "feature_dir": str(args.feature_dir),
        "output_dir": str(args.output_dir),
        "model_path": str(model_path),
        "onnx_path": str(onnx_path),
        "input_shape": input_shape,
        "train_samples": int(x_train.shape[0]),
        "test_samples": int(x_test.shape[0]),
        "epochs": args.epochs,
        "history": history,
    }
    (args.output_dir / "pilot_training_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
