from typing import Any, Callable, Dict, List

from django.conf import settings
from django.db import models
from django.db.models import signals
from django.forms import ValidationError

from pyava.parse import parseargs

from .json import Jsonify
from .utils import basenv, cached, cachewith


# Create your models here.


class TypeChoice(models.Model, Jsonify):

    class OptionChoices(models.IntegerChoices):
        GENERIC = 0, '通用'
        SYSTEM = 1, '系统'
        MANAGER = 2, '功能'
        MODULE = 3, '模块'

    type = models.AutoField("类型", primary_key=True)
    option = models.IntegerField('类型选项', choices=OptionChoices.choices)
    desc = models.CharField('分类描述', max_length=200)

    def __str__(self) -> str:
        return self.desc

    def json(self) -> dict:
        return {'type': self.type, 'option': self.option, 'desc': self.desc}

    class Meta:
        verbose_name = '测试分类'
        verbose_name_plural = '分类列表'


class Tool(models.Model, Jsonify):

    name = models.CharField('功能', max_length=200, help_text='功能名称')
    cmd = models.TextField('内容', blank=True, help_text='测试指令代码')
    type = models.ForeignKey(TypeChoice, on_delete=models.SET_DEFAULT,
                             default=None, verbose_name="分类", help_text="用于测试功能的区分和组合")
    update_time = models.DateTimeField("更新时间", auto_now=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    def __str__(self) -> str:
        return '<%03d><%s>...' % (self.id or 0, self.name)

    def json(self) -> Dict[str, str]:
        return {'id': self.id, 'name': self.name, 'code': self.cmd, 'args': self.args()}

    @property
    # @cached # Error pickle! TODO custom
    def code(self) -> Callable:
        exec(self.cmd, envs := Tool.codenv(self.id))
        if not callable(code := envs.get('code', None)):
            raise TypeError(f'{code!r} is not a callable code')
        return code

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
    
    @staticmethod
    def codenv(codeid=None):
        '''代码执行依赖环境'''
        if codeid == 0: # 基础依赖
            return basenv()
        base = Tool.objects.filter(id=0).first()
        if base is None:
            return basenv()
        return base.code()

    class Meta:
        verbose_name = '测试功能'
        verbose_name_plural = '测试列表'


class Server(models.Model, Jsonify):

    sid = models.IntegerField(verbose_name='服务器', primary_key=True)
    name = models.CharField(verbose_name='名称', max_length=200)
    host = models.GenericIPAddressField(verbose_name='地址', protocol='IPv4')
    port = models.IntegerField(verbose_name='端口', default=3334)

    def __str__(self) -> str:
        return f'{self.name}<{self.sid}>'

    def json(self) -> Dict[str, str]:
        return {'sid': self.sid, 'name': self.name}

    @property
    def agent_url(self):
        return 'http://%s:%d/%s' % (self.host, self.port, getattr(settings, 'AGENT_PATH', ''))

    class Meta:
        verbose_name = '服务器'
        verbose_name_plural = '服务器列表'
