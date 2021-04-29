# QT开发小笔记

## 安装

> 你看, 我就说不要用集成环境...

首先, 先安装anaconda;

其次, 新建一个env,然后安装pyside6

写一个测试小程序, 运行, 发现:

```

```

检查, 发现问题是这样的. pyside6找qt库, 但是定位到了anaconda自己带的qt库. 这个qt库是绘制anaconda自己的界面, 版本号和pyside自带的不同, 因此报错. 

因此, 解决方式不能将pyside的qt库替换到anaconda的qt库, 会导致anaconda界面和qtdesigner打不开; 而是让pyside找到自己的qt库.

所以, 切换到`anaconda3\envs\qtenv\lib\site-packages\PySide6`下, 打开__init__.py, 加入一下代码, 修改路径:

```
    dirname = os.path.dirname(__file__)
    plugin_path = os.path.join(dirname, 'plugins', 'platforms')
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
```

或者, 在Windows的环境变量界面(`ctrl+Q`)增加'QT_QPA_PLATFORM_PLUGIN_PATH': C:\Users\{UserName}\anaconda3\envs\qtenv\lib\site-packages\PySide6\plugins\platforms.

## 入门

> 2021年, 我所使用的pyside6被认为是最好的python界面绑定
> 许多鞋? 安装简单, 文档清楚, 兼容性好
> can't deny, it's true
> 但是竞争的库还是络绎不绝
> 总是给你一丝希望

如何评价一个库好不好? 很简单, 如果只看它的文档就能用, 那就是b（￣▽￣）d　
如果想要上手pyside6, 只需要转到![](https://wiki.qt.io/Main), 找到*Qt for Python*, 再看*Getting Started*
首先先看第四天*Tutorial*, 然后再看*official document*, 最后你就可以看着*API Reference*徒手写代码了
什么CSDN, 7天入门QT, 从入门到如土, 统统不需要. 

唯一的问题是, 即便API文档很全, 但是很多的描述含糊不清, 得需要一次次实验. 不过鉴于现在的版本才是`v6.0.3`, 所以还有很大的进步空间.

## Qt Designer

Qt Designer是用来**绘制**GUI界面的软件. 将**绘制**一词加粗的原因是, 除了排版调属性之外, 不要指望它进行信号的编辑. Qt Creator是新一代的界面绘制软件, 但是其内核还是Qt Designer. 所以在你安装完PySide6之后, 直接用其下自带的软件即可. 

> 注意, `anaconda3\envs\qtenv\lib\site-packages\PySide6`下的designer.exe不应该直接复制到桌面上, 而且--对于Windows系统--应该创建一个快捷方式. 因为这个软件依赖于文件夹下的一些库文件, 如果直接拷出来的话就没法用.

Qt Designer 有官方的手册, 这里需要只强调几个原则. 
* 所有的widget都应该放到layout中, 这样才可以响应窗口变化;
* 每新建一个widget都要修改ObjectName, 这个名字也是后面操纵组件时用的名字; 
* 不要手动修改生成的.ui文件, 这个文件应该只由designer生成. 除非designer做不到;

### widget放到layout中

    窗口组件都是组合成左右-上下的布局, 所以最方便的方式应该是先选中需要左右排列的小组件, horizontal一下, 然后再把竖着的组件vertical. 如果需要组件之间需要空隙, 只需要一个speacer隔开即可.

### 记得修改ObjectName

    我们知道Qt程序是一个QApplication类, 其上的ui会通过loader载入ui或引入转换后的代码. 所有由Qt designer设计出的widget都通过`window.objectName`来操作.


### 不要修改ui组件

    在designer中绘制完的界面保存为.ui文件, 然后使用pyside6的loader载入. 这样的好处是可以一边在designer上进行设计和修改, 一边在代码窗口进行调试. 每一次ctrl+s保存之后, .ui都会被覆盖, 所以如果直接修改.ui的话需要一遍遍再次修改. 如果designer实在没有提供这个操作, 应该在代码部分对载入后的.ui进行修改. 

## 开始写前端逻辑

    在我自己的实践中, 我觉得应该把前端窗口看作一个类, 这个类初始化的过程中首先应该初始化UI界面, 然后向每一个组件增加逻辑, 最后再初始化后端界面. 

```python
class Words:

    def __init__(self) -> None:
        self.app, self.window = self.initUI("words.ui", "debug")
        self.set_interaction_logic()
        self.backend = WordsBackend()
```

`initUI()`这一步是载入Qt designer绘制好的界面. 如果需要有什么修改, 或者增添designer做不到的功能, 都应该在这一部分混入.

```python
    def initUI(self, uiname, mode):
        # release mode
        # TODO: convert .ui to py code
        app = QApplication(sys.argv)

        # debug mode
        if mode == 'debug':
            ui_file_name = uiname
            ui_file = QFile(ui_file_name)
            if not ui_file.open(QIODevice.ReadOnly):
                print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
                sys.exit(-1)
            loader = QUiLoader()
            window = loader.load(ui_file)
            ui_file.close()
            if not window:
                print(loader.errorString())
                sys.exit(-1)
            window.show()

        return app, window
```

`set_interaction_logic()`向界面中的widget增加逻辑方法. 之前讲到, 尽量不用Qt designer设计信号, 而是在这一块手动增加, 这样检查起来会更加简单, 而不是再去.ui检查机器生成的代码. 

```python
    def set_interaction_logic(self):
        self.window.addButton.clicked.connect(self._on_add_click)
        self.window.removeButton.clicked.connect(self._on_remove_click)
```

`WordsBackend()`就是自己实现的后端, 负责实际的计算. 当点击界面的按钮, 逻辑方法就会调用后端的接口, 传入数据, 计算后得到值, 然后显示在界面上. 

具体的逻辑方法实现, 都是写在这个前端这个类的下面. 基本原理就是, 每当一个widget触发一个时间, 就会调用一个信号方法. 比如我点击`add`按钮:

相关的方法是`_on_add_click()`:

```python
    @Slot()
    def _on_add_click(self):
        pass
```

然后需要把方法绑定到`add`按钮上:

```python
    def set_interaction_logic(self):
        self.window.addButton.clicked.connect(self._on_add_click)
```

## QListWidget

`QListWidget`是`QListView`的进一步封装
