from typing import Callable, Dict, List

from django.db import models
from django.db.models import signals
from django.forms import ValidationError

from pytool.parse import parseargs

from .json import Jsonify
from .utils import cached, cachewith, codenv

# Create your models here.


class Tool(models.Model, Jsonify):

    class TypeChoices(models.IntegerChoices):
        GENERIC = 0, '通用'
        SYSTEM = 1, '系统'
        MANAGER = 2, '功能'
        MODULE = 3, '模块'

    name = models.CharField('功能', max_length=200, help_text='功能名称')
    cmd = models.TextField('内容', blank=True, help_text='测试指令代码')
    type = models.IntegerField(
        "类型分类", choices=TypeChoices.choices, default=TypeChoices.GENERIC, help_text='功能分类')
    update_time = models.DateTimeField("更新时间", auto_now=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    def __str__(self) -> str:
        return '<%03d><%s>...' % (self.id or 0, self.name)

    def json(self) -> Dict[str, str]:
        return {'id': self.id, 'name': self.name, 'code': self.cmd, 'args': self.args()}

    @property
    # @cached # Error pickle! TODO custom
    def code(self) -> Callable:
        exec(self.cmd, envs := codenv())
        if not callable(code := envs.get('code', None)):
            raise TypeError(f'{code!r} is not a callable code')
        return code

    @cachewith('back.Tool', (signals.post_save, signals.post_delete))
    def args(self) -> List[Dict[str, str]]:
        '''
        ```ts
        arg = {name: ..., type?: ..., default?: ..., desc?: ...}
        ```
        '''
        return parseargs(self.code)

    def clean(self) -> None:
        try:
            self.code
        except BaseException as e:
            raise ValidationError(e)

    class Meta:
        verbose_name = '测试功能'
        verbose_name_plural = '测试列表'


class Server(models.Model):
    sid = models.IntegerField(verbose_name='服务器', primary_key=True)
    name = models.CharField(verbose_name='名称', max_length=200)
    host = models.GenericIPAddressField(verbose_name='地址', protocol='IPv4', null=False)
    port = models.IntegerField(verbose_name='端口', default=3334)

    def __str__(self) -> str:
        return f'{self.name}<{self.sid}>'

    class Meta:
        verbose_name = '服务器'
        verbose_name_plural = '服务器列表'
