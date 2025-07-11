# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
import argparse

import torch

from .models import build_ACT_model_, build_ACT_YHD_model_, build_CNNMLP_model_


def get_args_parser():
    parser = argparse.ArgumentParser("Set transformer detector", add_help=False)
    parser.add_argument("--lr", default=1e-4, type=float)  # will be overridden
    parser.add_argument("--lr_backbone", default=1e-5, type=float)  # will be overridden
    parser.add_argument("--batch_size", default=2, type=int)  # not used
    parser.add_argument("--weight_decay", default=1e-4, type=float)
    parser.add_argument("--epochs", default=300, type=int)  # not used
    parser.add_argument("--lr_drop", default=200, type=int)  # not used
    parser.add_argument(
        "--clip_max_norm",
        default=0.1,
        type=float,  # not used
        help="gradient clipping max norm",
    )

    # Model parameters
    # * Backbone
    parser.add_argument(
        "--backbone",
        default="resnet18",
        type=str,  # will be overridden
        help="Name of the convolutional backbone to use",
    )
    parser.add_argument(
        "--dilation",
        action="store_true",
        help="If true, we replace stride with dilation in the last convolutional block (DC5)",
    )
    parser.add_argument(
        "--position_embedding",
        default="sine",
        type=str,
        choices=("sine", "learned"),
        help="Type of positional embedding to use on top of the image features",
    )
    parser.add_argument(
        "--camera_names",
        default=[],
        type=list,  # will be overridden
        help="A list of camera names",
    )

    # * Transformer
    parser.add_argument(
        "--enc_layers",
        default=4,
        type=int,  # will be overridden
        help="Number of encoding layers in the transformer",
    )
    parser.add_argument(
        "--dec_layers",
        default=6,
        type=int,  # will be overridden
        help="Number of decoding layers in the transformer",
    )
    parser.add_argument(
        "--dim_feedforward",
        default=2048,
        type=int,  # will be overridden
        help="Intermediate size of the feedforward layers in the transformer blocks",
    )
    parser.add_argument(
        "--hidden_dim",
        default=256,
        type=int,  # will be overridden
        help="Size of the embeddings (dimension of the transformer)",
    )
    parser.add_argument(
        "--dropout", default=0.1, type=float, help="Dropout applied in the transformer"
    )
    parser.add_argument(
        "--nheads",
        default=8,
        type=int,  # will be overridden
        help="Number of attention heads inside the transformer's attentions",
    )
    parser.add_argument(
        "--num_queries",
        default=400,
        type=int,  # will be overridden
        help="Number of query slots",
    )
    parser.add_argument("--pre_norm", action="store_true")

    # * Segmentation
    parser.add_argument(
        "--masks",
        action="store_true",
        help="Train segmentation head if the flag is provided",
    )
    return parser


def build_ACT_model(args_override):
    parser = argparse.ArgumentParser(
        "DETR training and evaluation script", parents=[get_args_parser()]
    )
    args, unkown = parser.parse_known_args()

    for k, v in args_override.items():
        setattr(args, k, v)

    model = build_ACT_model_(args)
    model.cuda()

    return model, args


def build_ACT_YHD_model(config, args_override):
    parser = argparse.ArgumentParser(
        "DETR training and evaluation script", parents=[get_args_parser()]
    )
    args, unkown = parser.parse_known_args()

    for k, v in args_override.items():
        setattr(args, k, v)

    model = build_ACT_YHD_model_(config, args)
    model.cuda()

    return model, args


def build_CNNMLP_model(args_override):
    parser = argparse.ArgumentParser(
        "DETR training and evaluation script", parents=[get_args_parser()]
    )
    args, unkown = parser.parse_known_args()

    for k, v in args_override.items():
        setattr(args, k, v)

    model = build_CNNMLP_model_(args)
    model.cuda()

    return model, args


def build_optimizer(model, args):
    param_dicts = [  # TDOO
        {
            "params": [
                p
                for n, p in model.named_parameters()
                if "backbone" not in n and p.requires_grad
            ]
        },
        {
            "params": [
                p
                for n, p in model.named_parameters()
                if "backbone" in n and p.requires_grad
            ],
            "lr": args.lr_backbone,
        },
    ]
    # TODO: use lr to build an optimizer
    # 优化器传入的args应该是训练参数，而不是模型参数
    # 根据训练时的学习率来生成训练时对应的优化器
    optimizer = torch.optim.AdamW(
        param_dicts, lr=args.lr, weight_decay=args.weight_decay
    )
    return optimizer


def build_ACT_model_and_optimizer(args_override):
    model, args = build_ACT_model(args_override)
    optimizer = build_optimizer(model, args)
    return model, optimizer


def build_CNNMLP_model_and_optimizer(args_override):
    model, args = build_CNNMLP_model(args_override)
    optimizer = build_optimizer(model, args)
    return model, optimizer
