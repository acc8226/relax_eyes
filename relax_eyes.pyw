"""
This program reminds you to relax after working for a certain period.

Copyright © 2020-2022 <Harper Liu, https://github.com/shuangye/relax_eyes>
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import sys
import webbrowser
from datetime import datetime
from tkinter import *
from tkinter import messagebox

g_root = None

# 工作时间 单位秒
g_workDuration = 20
# 休息实际 单位秒
g_relaxDuration = 10
# 正常切换为休息状态前的第 5 秒会提醒
g_notifyDurationBeforeRelax = 5

# 循环间隔 单位秒
gc_TIMER_RESOLUTION = 1

gc_FONT = '黑体'

gc_DEFAULT_BG_COLOR = '#DDDDDD'
gc_DEFAULT_FG_COLOR = 'black'
gc_RELAX_FG_COLOR = gc_DEFAULT_BG_COLOR
gc_RELAX_BG_COLOR = gc_DEFAULT_FG_COLOR

gc_NOTIFY_FG_COLOR = 'orange'

gc_REPO_URL = 'https://github.com/shuangye/relax_eyes'

gc_MODE_RELAX = 0
gc_MODE_WORK = 1

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.initSelf(master)
        self.createWidgets()
        self.configureUI(False)
        # 不停的进行循环
        self.timeMeas()
        # 快捷键绑定
        master.bind("<Escape>", self.escape)
        master.bind("<F11>", self.toggleFullscreen)

    def escape(self, event=None):
        # 全屏状态
        if self.fullscreenState == True:
            if self.mode == gc_MODE_RELAX:
                self.work(True)                    
            else:
                self.exitFullscreen()
        else:
            # 正常窗口状态
            ret = messagebox.askyesno("提示", "是否退出?")
            if ret:
                self.root.destroy()

    def toggleFullscreen(self, event=None):
        self.fullscreenState = not self.fullscreenState
        self.root.attributes("-fullscreen", self.fullscreenState)
    
    def toFullscreen(self):
        self.fullscreenState = True
        self.root.attributes("-fullscreen", self.fullscreenState)

    def exitFullscreen(self):
        self.fullscreenState = False
        self.root.attributes("-fullscreen", self.fullscreenState)

    def initSelf(self, master=None):
        self.root = master
        # 当前模式默认是工作模式
        self.mode = gc_MODE_WORK
        # 剩余秒数为 0
        self.lapsed = 0
        self.countdownText = StringVar()
        self.currentTime = StringVar()
        self.fullscreenState = False
        # 调用父类的 2 方法，设置该 frame
        self.pack(expand=True, fill='both')
        self.place(in_=master, anchor=CENTER, relx=0.5, rely=0.5)

    def createWidgets(self):
        self.statusLabel = Label(self, font=(gc_FONT, 30), pady=20)
        self.statusLabel.pack()

        self.countdownLabel = Label(self, font=(
            gc_FONT, 100), textvariable=self.countdownText, pady=30)
        self.countdownLabel.pack()

        self.currentTimeLabel = Label(self, font=(
            gc_FONT, 35), textvariable=self.currentTime, pady=30)
        self.currentTimeLabel.pack()

        self.bottomFrame = Frame(master=self.master)
        self.bottomFrame.pack(expand=True, fill=X, anchor=S, side=BOTTOM)

        self.copyLabel = Label(self.bottomFrame, font=(
            gc_FONT, 10), text='© 2020-2022 <Harper LIU, {0}>'.format(gc_REPO_URL), cursor="hand2")
        self.copyLabel.pack(side=LEFT, anchor=SW)
        self.copyLabel.bind(
            "<Button-1>", lambda e: webbrowser.open_new(gc_REPO_URL))

        self.actionButton = Button(self.bottomFrame, font=(
            gc_FONT, 20), command=self.relax, borderwidth=0, padx=10, pady=10)
        self.actionButton.pack(side=RIGHT, anchor=SE)

    # 根据 self.mode 进行 UI 配置
    def configureUI(self, isAuto=False):
        if self.mode == gc_MODE_RELAX:
            bgColor = gc_RELAX_BG_COLOR
            fgColor = gc_RELAX_FG_COLOR
            statusLebel = '剩余休息时间'
        else:
            # 一进入则是工作状态
            bgColor = gc_DEFAULT_BG_COLOR
            fgColor = gc_DEFAULT_FG_COLOR
            statusLebel = '剩余工作时间'
        # 颜色配置
        g_root.configure(bg=bgColor)
        self.configure(bg=bgColor)
        self.statusLabel.configure(bg=bgColor, fg=fgColor, text=statusLebel)
        self.countdownLabel.configure(bg=bgColor, fg=fgColor)
        self.currentTimeLabel.configure(bg=bgColor, fg=fgColor)
        self.bottomFrame.configure(bg=bgColor)
        self.copyLabel.configure(bg=bgColor, fg=fgColor)

        # 如果当前是休息状态
        if self.mode == gc_MODE_RELAX:
            self.actionButton.configure(
                bg=bgColor, fg=fgColor, text='继续工作', command=self.work)
            self.bringUpWindow(True)
        else:
            # 如果当前是工作状态
            self.actionButton.configure(
                bg=bgColor, fg=fgColor, text='立刻休息', command=self.relax)
            # 如果是非自动（手动）则最小化
            if isAuto:
                g_root.wm_state('iconic')
            else:
                self.exitFullscreen()

    def timeMeas(self):
        # 如果当前是休息模式
        if (self.mode == gc_MODE_RELAX):
            # 进入下一个状态所需的秒数
            remaining = g_relaxDuration - self.lapsed
            if remaining <= 0:
                # 自动进入工作状态
                self.work(True)
        # 如果当前是工作模式
        else:
            remaining = g_workDuration - self.lapsed
            # 如果还剩 20 秒将进入休息状态，这里最好是弹出通知比较好
            if remaining <= 0:
                # 自动进入休息状态
                self.relax(True)
            elif remaining <= g_notifyDurationBeforeRelax:
                # 倒计时弹窗
                if remaining == g_notifyDurationBeforeRelax:
                    self.bringUpWindow(False)
                # 字符变色闪烁
                if remaining % 2 == 0:
                    self.countdownLabel.configure(fg='red')
                else:
                    self.countdownLabel.configure(fg=gc_NOTIFY_FG_COLOR)
        # 更新倒计时：还剩下 x 分 y 秒
        self.countdownText.set("{0:02}:{1:02}".format(
            remaining // 60, remaining % 60))
        # 更新当前时间
        self.currentTime.set(datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        # 继续循环
        if remaining > 0:
            self.lapsed += gc_TIMER_RESOLUTION
            self.after(gc_TIMER_RESOLUTION * 1000, self.timeMeas)
        else:
            self.after(1, self.timeMeas)

    # 是否是临时的
    def bringUpWindow(self, isFullscreen=False):
        g_root.update()
        g_root.deiconify()
        g_root.lift()
        g_root.attributes('-topmost', True)
        if isFullscreen:
            self.toFullscreen()
        else:
            self.exitFullscreen()

    def work(self, isAuto=False):
        # 刷新工作状态
        self.mode = gc_MODE_WORK
        self.lapsed = 0
        self.configureUI(isAuto)

    def relax(self, isAuto=False):
        # 刷新工作状态
        self.mode = gc_MODE_RELAX
        self.lapsed = 0
        self.configureUI(isAuto)

def main():
    global g_root
    # 创建窗口：实例化一个窗口对象。
    g_root = Tk()
    # 设置标题
    g_root.title('Relax Eyes')
    g_root.resizable(True, True)
    # 窗口大小
    winfo_screenwidth = 660
    winfo_screenheight = 470
    g_root.geometry("{}x{}".format(winfo_screenwidth, winfo_screenheight))
    g_root.configure(bg=gc_DEFAULT_BG_COLOR)
    app = Application(master=g_root)
    # 进入消息循环
    app.mainloop()

if __name__ == "__main__":
    # specify duration in minutes
    if len(sys.argv) >= 3:
        g_workDuration = int(sys.argv[1]) * 60
        g_relaxDuration = int(sys.argv[2]) * 60
    main()
