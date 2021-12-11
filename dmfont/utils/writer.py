"""
DMFont
Copyright (c) 2020-present NAVER Corp.
MIT license
"""
from pathlib import Path
import torch.nn.functional as F
from . import save_tensor_to_image


class Writer:
    def add_scalars(self, tag_scalar_dic, global_step):
        raise NotImplementedError()

    def add_image(self, tag, img_tensor, global_step):
        raise NotImplementedError()


class DiskWriter(Writer):
    def __init__(self, img_path, scale=None):
        self.img_dir = Path(img_path)
        self.img_dir.mkdir(parents=True, exist_ok=True)
        self.scale = scale

    def add_scalars(self, tag_scalar_dic, global_step):
        pass

    def add_image(self, tag, img_tensor, global_step):
        path = self.img_dir / "{:07d}-{}.png".format(global_step, tag)
        save_tensor_to_image(img_tensor, path, self.scale)


class TBWriter(Writer):
    def __init__(self, dir_path, scale=None):
        from tensorboardX import SummaryWriter
        self.writer = SummaryWriter(dir_path, flush_secs=30)
        self.scale = scale

    def add_scalars(self, tag_scalar_dic, global_step):
        for tag, scalar in tag_scalar_dic.items():
            self.writer.add_scalar(tag, scalar, global_step)

    def add_image(self, tag, img_tensor, global_step):
        if self.scale:
            img_tensor = F.interpolate(
                img_tensor.unsqueeze(0), scale_factor=self.scale, mode='bilinear',
                align_corners=False
            ).squeeze(0)
        self.writer.add_image(tag, img_tensor, global_step)


class TBDiskWriter(TBWriter):
    def __init__(self, dir_path, img_path, scale=None):
        super().__init__(dir_path)
        # composition
        self._disk_writer = DiskWriter(img_path, scale)

    def add_image(self, tag, img_tensor, global_step):
        return self._disk_writer.add_image(tag, img_tensor, global_step)
