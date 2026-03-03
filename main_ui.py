import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
import numpy as np
import cv2
from image_enhancement import enhance_image
from image_rotation import rotate_image
from image_cropping import crop_image


class FiberProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("光纤锥图像处理系统")
        self.root.geometry("550x750")  # 高度略微增加以容纳新控件
        self.root.resizable(True, True)

        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=('微软雅黑', 10))
        self.style.configure("TLabel", font=('微软雅黑', 10))
        self.style.configure("TEntry", font=('微软雅黑', 10))
        self.style.configure("TCheckbutton", font=('微软雅黑', 10))

        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 功能选择
        self.function_frame = ttk.LabelFrame(self.main_frame, text="处理功能", padding=10)
        self.function_frame.pack(fill=tk.X, pady=10)

        # 功能复选框
        self.enhance_var = tk.BooleanVar(value=True)
        self.rotate_var = tk.BooleanVar(value=True)
        self.crop_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(self.function_frame, text="图像增强", variable=self.enhance_var).grid(row=0, column=0, padx=10,
                                                                                              sticky='w')
        ttk.Checkbutton(self.function_frame, text="图像旋转", variable=self.rotate_var).grid(row=0, column=1, padx=10,
                                                                                             sticky='w')
        ttk.Checkbutton(self.function_frame, text="图像裁剪", variable=self.crop_var).grid(row=0, column=2, padx=10,
                                                                                           sticky='w')

        # 输入文件夹选择
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, pady=5)

        ttk.Label(self.input_frame, text="输入文件夹:").grid(row=0, column=0, padx=(0, 10), sticky='e')
        self.input_entry = ttk.Entry(self.input_frame, width=40)
        self.input_entry.grid(row=0, column=1, sticky='we', padx=(0, 10))
        ttk.Button(self.input_frame, text="浏览...", command=self.select_input_folder).grid(row=0, column=2)

        # 输出文件夹选择
        self.output_frame = ttk.Frame(self.main_frame)
        self.output_frame.pack(fill=tk.X, pady=5)

        ttk.Label(self.output_frame, text="输出文件夹:").grid(row=0, column=0, padx=(0, 10), sticky='e')
        self.output_entry = ttk.Entry(self.output_frame, width=40)
        self.output_entry.grid(row=0, column=1, sticky='we', padx=(0, 10))
        ttk.Button(self.output_frame, text="浏览...", command=self.select_output_folder).grid(row=0, column=2)

        # 旋转设置
        self.rotation_frame = ttk.LabelFrame(self.main_frame, text="旋转设置", padding=10)
        self.rotation_frame.pack(fill=tk.X, pady=10)

        # 头结点序号
        ttk.Label(self.rotation_frame, text="头结点序号:").grid(row=0, column=0, padx=(0,10), sticky='e')
        self.center_number_entry = ttk.Entry(self.rotation_frame, width=10)
        self.center_number_entry.grid(row=0, column=1, sticky='w')
        self.center_number_entry.insert(0, "1")
        ttk.Label(self.rotation_frame, text="(1表示最大光斑, 2表示第二大, 以此类推)").grid(row=0, column=2, padx=(10,0), sticky='w')

        # 固定角度旋转
        self.fixed_angle_var = tk.BooleanVar(value=False)
        self.fixed_angle_check = ttk.Checkbutton(self.rotation_frame, text="使用固定角度旋转", variable=self.fixed_angle_var)
        self.fixed_angle_check.grid(row=1, column=0, columnspan=2, sticky='w', pady=(5,0))

        self.fixed_angle_entry = ttk.Entry(self.rotation_frame, width=10, state='disabled')
        self.fixed_angle_entry.grid(row=1, column=2, sticky='w', padx=(10,0))
        ttk.Label(self.rotation_frame, text="度").grid(row=1, column=3, sticky='w')

        self.fixed_angle_var.trace('w', self.toggle_fixed_angle_entry)

        # 比例设置（裁剪）
        self.proportion_frame = ttk.LabelFrame(self.main_frame, text="裁剪设置", padding=10)
        self.proportion_frame.pack(fill=tk.X, pady=10)

        ttk.Label(self.proportion_frame, text="中心点比例:").grid(row=0, column=0, padx=(0, 10), sticky='e')
        self.proportion_entry = ttk.Entry(self.proportion_frame, width=10)
        self.proportion_entry.grid(row=0, column=1, sticky='w')
        self.proportion_entry.insert(0, "0.5")

        ttk.Label(self.proportion_frame, text="(0-1之间，0.5表示中心，0.67表示2/3位置)").grid(row=0, column=2,
                                                                                            padx=(10, 0), sticky='w')

        # 处理按钮
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=20)

        self.process_btn = ttk.Button(self.button_frame, text="开始处理", command=self.start_processing)
        self.process_btn.pack(pady=10)

        # 进度条
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress_frame.pack(fill=tk.X, pady=10)

        self.progress_label = ttk.Label(self.progress_frame, text="就绪")
        self.progress_label.pack(fill=tk.X)

        self.progress = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X)

        # 结果表格
        self.result_frame = ttk.LabelFrame(self.main_frame, text="处理结果", padding=10)
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 创建树形视图
        self.tree = ttk.Treeview(self.result_frame, columns=('status', 'message'), show='headings')
        self.tree.heading('#0', text='文件名')
        self.tree.heading('status', text='状态')
        self.tree.heading('message', text='消息')
        self.tree.column('#0', width=200)
        self.tree.column('status', width=80, anchor=tk.CENTER)
        self.tree.column('message', width=250)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 状态变量
        self.processing = False
        self.original_sizes = {}  # 存储原始图像尺寸

    def select_input_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, folder_selected)

            # 自动设置输出文件夹
            parent_dir, folder_name = os.path.split(folder_selected.rstrip(os.sep))
            output_dir = os.path.join(parent_dir, f"{folder_name}_预处理结果")
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, output_dir)

    def select_output_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder_selected)

    def toggle_fixed_angle_entry(self, *args):
        """根据复选框状态启用/禁用角度输入框"""
        if self.fixed_angle_var.get():
            self.fixed_angle_entry.config(state='normal')
        else:
            self.fixed_angle_entry.config(state='disabled')

    def start_processing(self):
        if self.processing:
            return

        input_dir = self.input_entry.get()
        output_dir = self.output_entry.get()
        proportion_str = self.proportion_entry.get().strip()

        # 获取功能选择
        do_enhance = self.enhance_var.get()
        do_rotate = self.rotate_var.get()
        do_crop = self.crop_var.get()

        # 获取旋转参数
        center_number_str = self.center_number_entry.get().strip()
        fixed_angle_checked = self.fixed_angle_var.get()
        fixed_angle_str = self.fixed_angle_entry.get().strip() if fixed_angle_checked else None

        # 验证输入
        errors = []
        if not input_dir:
            errors.append("请选择输入文件夹")
        if not output_dir:
            errors.append("请选择输出文件夹")
        if not (do_enhance or do_rotate or do_crop):
            errors.append("请至少选择一个处理功能")

        # 验证头结点序号
        try:
            center_number = int(center_number_str) if center_number_str else 1
            if center_number < 1:
                raise ValueError("头结点序号必须大于等于1")
        except ValueError:
            errors.append("头结点序号必须为正整数")

        # 验证固定角度
        fixed_angle = None
        if fixed_angle_checked:
            if fixed_angle_str:
                try:
                    fixed_angle = float(fixed_angle_str)
                except ValueError:
                    errors.append("固定角度必须为数字")
            else:
                errors.append("请填写固定角度值")

        # 验证比例（如果启用裁剪）
        if do_crop:
            try:
                proportion = float(proportion_str)
                if not 0 < proportion < 1:
                    raise ValueError("比例必须在0和1之间")
            except ValueError as e:
                errors.append(f"无效的比例值: {str(e)}")

        if errors:
            messagebox.showerror("输入错误", "\n".join(errors))
            return

        # 清空结果列表和原始尺寸记录
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.original_sizes = {}

        # 更新UI状态
        self.processing = True
        self.process_btn.config(state=tk.DISABLED)
        self.progress_label.config(text="处理中...")
        self.progress['value'] = 0

        # 在后台线程中处理
        threading.Thread(
            target=self.process_images,
            args=(input_dir, output_dir, proportion_str, do_enhance, do_rotate, do_crop,
                  center_number, fixed_angle),
            daemon=True
        ).start()

    def process_images(self, input_dir, output_dir, proportion_str, do_enhance, do_rotate, do_crop,
                       center_number, fixed_angle):
        try:
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)

            # 获取图像文件列表
            image_files = [f for f in os.listdir(input_dir)
                           if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp'))]

            if not image_files:
                self.root.after(10, self.show_error, "文件夹中没有找到任何图像文件")
                return

            total_files = len(image_files)
            processed_count = 0

            # 处理每个文件
            for filename in image_files:
                input_path = os.path.join(input_dir, filename)
                output_path = os.path.join(output_dir, filename)

                try:
                    # 读取图像
                    if self.contains_chinese(input_path):
                        img = cv2.imdecode(np.fromfile(input_path, dtype=np.uint8), -1)
                    else:
                        img = cv2.imread(input_path, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_GRAYSCALE)

                    if img is None:
                        raise ValueError(f"无法读取图像: {filename}")

                    # 记录原始尺寸
                    self.original_sizes[filename] = img.shape[1], img.shape[0]

                    # 处理流程
                    processed = img.copy()
                    rotation_center = None  # 用于存储旋转后的头结点坐标

                    # 1. 图像增强
                    if do_enhance:
                        processed = enhance_image(processed)

                    # 2. 图像旋转
                    if do_rotate:
                        processed, rotation_center = rotate_image(
                            processed,
                            center_number=center_number,
                            fixed_angle=fixed_angle,
                            spot_thresh=16,
                            line_thresh=16,
                            draw_contour=True
                        )

                    # 3. 图像裁剪
                    if do_crop:
                        if rotation_center is None:
                            # 旋转未找到头结点，无法裁剪，记录警告
                            self.root.after(10, self.update_progress, filename, False,
                                            "旋转未找到头结点，跳过裁剪", (processed_count + 0.5) / total_files * 100)
                        else:
                            # 获取原始尺寸
                            orig_width, orig_height = self.original_sizes[filename]
                            # 计算目标尺寸（原图一半）
                            target_width = orig_width // 2
                            target_height = orig_height // 2
                            # 解析比例
                            proportion = float(proportion_str)
                            # 裁剪图像
                            processed = crop_image(processed, target_width, target_height,
                                                   rotation_center, proportion)

                    # 保存处理结果
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    # 兼容中文/特殊字符路径
                    if self.contains_chinese(output_path):
                        cv2.imencode('.jpg', processed)[1].tofile(output_path)
                    else:
                        cv2.imwrite(output_path, processed)

                    # 更新进度
                    processed_count += 1
                    progress = (processed_count / total_files) * 100
                    self.root.after(10, self.update_progress, filename, True, "", progress)

                except Exception as e:
                    processed_count += 1
                    progress = (processed_count / total_files) * 100
                    self.root.after(10, self.update_progress, filename, False, str(e), progress)

            self.root.after(10, self.finish_processing, True, "处理完成!")

        except Exception as e:
            self.root.after(10, self.show_error, str(e))

    @staticmethod
    def contains_chinese(text):
        return any('\u4e00' <= ch <= '\u9fff' for ch in text)

    def update_progress(self, filename, success, message, progress_value):
        # 更新进度条
        self.progress['value'] = progress_value
        self.progress_label.config(text=f"处理中: {int(progress_value)}%")

        # 添加结果到列表
        status = "成功" if success else "失败"
        item_id = self.tree.insert('', 'end', text=filename, values=(status, message))

        # 滚动到最后
        self.tree.see(item_id)
        self.tree.update()

    def finish_processing(self, success, message):
        self.processing = False
        self.process_btn.config(state=tk.NORMAL)

        if success:
            self.progress_label.config(text=message)
            messagebox.showinfo("完成", message)
        else:
            self.progress_label.config(text="处理失败")

    def show_error(self, message):
        self.processing = False
        self.process_btn.config(state=tk.NORMAL)
        self.progress_label.config(text="处理失败")
        messagebox.showerror("错误", message)


if __name__ == "__main__":
    root = tk.Tk()
    app = FiberProcessorApp(root)
    root.mainloop()