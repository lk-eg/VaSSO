from utils.register import Registry
from utils.device import device


MODELS_REGISTRY = Registry("Models")


def build_model(args):
    model = MODELS_REGISTRY.get(args.model)(args)
    model = model.to(device)
    return model
