from . import GridLayout, Image

class Background_GridLayout(GridLayout):
    def __init__(self, **kwargs):
        super(Background_GridLayout, self).__init__(**kwargs)
        
        # 添加背景图片
        #with self.canvas.before:
        #    self.bg = Image(source='./images/图片3.jpg', allow_stretch=True, keep_ratio=False)
        #    self.bind(size=self._update_bg, pos=self._update_bg)

    def _update_bg(self, instance, value):
        # 更新背景图片的位置和大小，以确保与 Layout 保持一致
        self.bg.pos = self.pos
        self.bg.size = self.size

