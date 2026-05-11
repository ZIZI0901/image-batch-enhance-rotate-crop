from __future__ import annotations

from pathlib import Path
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from image_batch_enhance_rotate_crop.processor import (
    ProcessingOptions,
    ProcessingResult,
    process_folder,
)


class ImageProcessorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("批量图像增强、旋转与裁剪")
        self.root.geometry("720x860")
        self.root.minsize(700, 780)
        self.processing = False
        self._build_widgets()

    def _build_widgets(self) -> None:
        style = ttk.Style()
        style.configure("TButton", padding=6, font=("Microsoft YaHei UI", 10))
        style.configure("TLabel", font=("Microsoft YaHei UI", 10))
        style.configure("TEntry", font=("Microsoft YaHei UI", 10))
        style.configure("TCheckbutton", font=("Microsoft YaHei UI", 10))

        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        function_frame = ttk.LabelFrame(main_frame, text="处理功能", padding=10)
        function_frame.pack(fill=tk.X, pady=8)

        self.enhance_var = tk.BooleanVar(value=True)
        self.rotate_var = tk.BooleanVar(value=True)
        self.crop_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(function_frame, text="图像增强", variable=self.enhance_var).grid(row=0, column=0, padx=10, sticky="w")
        ttk.Checkbutton(function_frame, text="图像旋转", variable=self.rotate_var).grid(row=0, column=1, padx=10, sticky="w")
        ttk.Checkbutton(function_frame, text="图像裁剪", variable=self.crop_var).grid(row=0, column=2, padx=10, sticky="w")

        self.input_entry = self._folder_row(main_frame, "输入文件夹", self.select_input_folder)
        self.output_entry = self._folder_row(main_frame, "输出文件夹", self.select_output_folder)

        enhance_frame = ttk.LabelFrame(main_frame, text="增强参数", padding=10)
        enhance_frame.pack(fill=tk.X, pady=8)
        self.brightness_entry = self._numeric_entry(enhance_frame, "亮度倍数", "1.2", row=0, col=0)
        self.contrast_entry = self._numeric_entry(enhance_frame, "对比度倍数", "1.5", row=0, col=2)

        rotation_frame = ttk.LabelFrame(main_frame, text="旋转参数", padding=10)
        rotation_frame.pack(fill=tk.X, pady=8)
        self.center_number_entry = self._numeric_entry(rotation_frame, "亮斑序号", "1", row=0, col=0)
        ttk.Label(rotation_frame, text="1 为最大亮斑，2 为第二大亮斑").grid(row=0, column=2, padx=(10, 18), sticky="w")

        self.spot_threshold_entry = self._numeric_entry(rotation_frame, "亮斑阈值", "16", row=1, col=0)
        self.line_threshold_entry = self._numeric_entry(rotation_frame, "主轴阈值", "16", row=1, col=2)

        self.fixed_angle_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            rotation_frame,
            text="使用固定角度旋转",
            variable=self.fixed_angle_var,
            command=self.toggle_fixed_angle_entry,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self.fixed_angle_entry = ttk.Entry(rotation_frame, width=10, state="disabled")
        self.fixed_angle_entry.grid(row=2, column=2, sticky="w", padx=(10, 0), pady=(8, 0))
        ttk.Label(rotation_frame, text="度").grid(row=2, column=3, sticky="w", pady=(8, 0))

        self.draw_reference_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(rotation_frame, text="绘制参考线和中心点", variable=self.draw_reference_var).grid(
            row=3,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(8, 0),
        )

        crop_frame = ttk.LabelFrame(main_frame, text="裁剪参数", padding=10)
        crop_frame.pack(fill=tk.X, pady=8)
        self.proportion_entry = self._numeric_entry(crop_frame, "中心水平比例", "0.5", row=0, col=0)
        self.crop_scale_entry = self._numeric_entry(crop_frame, "裁剪尺寸比例", "0.5", row=0, col=2)
        ttk.Label(crop_frame, text="中心比例 0.5 为居中；尺寸比例 0.5 为裁剪原图一半宽高").grid(
            row=1,
            column=0,
            columnspan=4,
            sticky="w",
            pady=(8, 0),
        )

        self.process_btn = ttk.Button(main_frame, text="开始处理", command=self.start_processing)
        self.process_btn.pack(pady=12)

        self.progress_label = ttk.Label(main_frame, text="就绪")
        self.progress_label.pack(fill=tk.X)
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(4, 12))

        result_frame = ttk.LabelFrame(main_frame, text="处理结果", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(result_frame, columns=("status", "message"), show="tree headings")
        self.tree.heading("#0", text="文件名")
        self.tree.heading("status", text="状态")
        self.tree.heading("message", text="消息")
        self.tree.column("#0", width=240)
        self.tree.column("status", width=90, anchor=tk.CENTER)
        self.tree.column("message", width=320)

        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def _folder_row(self, parent: ttk.Frame, label: str, command) -> ttk.Entry:
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        ttk.Label(frame, text=label).grid(row=0, column=0, padx=(0, 10), sticky="e")
        entry = ttk.Entry(frame, width=54)
        entry.grid(row=0, column=1, sticky="we", padx=(0, 10))
        frame.columnconfigure(1, weight=1)
        ttk.Button(frame, text="浏览...", command=command).grid(row=0, column=2)
        return entry

    def _numeric_entry(self, parent: ttk.Frame, label: str, default: str, row: int, col: int) -> ttk.Entry:
        ttk.Label(parent, text=label).grid(row=row, column=col, padx=(0, 10), pady=4, sticky="e")
        entry = ttk.Entry(parent, width=10)
        entry.grid(row=row, column=col + 1, padx=(0, 18), pady=4, sticky="w")
        entry.insert(0, default)
        return entry

    def select_input_folder(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, folder)
            input_path = Path(folder)
            output_path = input_path.with_name(f"{input_path.name}_预处理结果")
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, str(output_path))

    def select_output_folder(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder)

    def toggle_fixed_angle_entry(self) -> None:
        state = "normal" if self.fixed_angle_var.get() else "disabled"
        self.fixed_angle_entry.config(state=state)

    def start_processing(self) -> None:
        if self.processing:
            return

        try:
            options = self._collect_options()
            input_dir = self.input_entry.get().strip()
            output_dir = self.output_entry.get().strip()
            if not input_dir:
                raise ValueError("请选择输入文件夹")
            if not output_dir:
                raise ValueError("请选择输出文件夹")
        except ValueError as exc:
            messagebox.showerror("输入错误", str(exc))
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.processing = True
        self.process_btn.config(state=tk.DISABLED)
        self.progress_label.config(text="处理中...")
        self.progress["value"] = 0

        threading.Thread(
            target=self._run_processing,
            args=(input_dir, output_dir, options),
            daemon=True,
        ).start()

    def _collect_options(self) -> ProcessingOptions:
        if not (self.enhance_var.get() or self.rotate_var.get() or self.crop_var.get()):
            raise ValueError("请至少选择一个处理功能")

        brightness = self._read_float(self.brightness_entry, "亮度倍数")
        contrast = self._read_float(self.contrast_entry, "对比度倍数")
        if brightness <= 0:
            raise ValueError("亮度倍数必须大于 0")
        if contrast <= 0:
            raise ValueError("对比度倍数必须大于 0")

        center_number = self._read_int(self.center_number_entry, "亮斑序号")
        if center_number < 1:
            raise ValueError("亮斑序号必须大于等于 1")

        spot_threshold = self._read_int(self.spot_threshold_entry, "亮斑阈值")
        line_threshold = self._read_int(self.line_threshold_entry, "主轴阈值")
        if not 0 <= spot_threshold <= 255:
            raise ValueError("亮斑阈值必须在 0 到 255 之间")
        if not 0 <= line_threshold <= 255:
            raise ValueError("主轴阈值必须在 0 到 255 之间")

        fixed_angle = None
        if self.fixed_angle_var.get():
            fixed_angle = self._read_float(self.fixed_angle_entry, "固定角度")

        crop_proportion = self._read_float(self.proportion_entry, "中心水平比例")
        if not 0 < crop_proportion < 1:
            raise ValueError("中心水平比例必须在 0 和 1 之间")

        crop_scale = self._read_float(self.crop_scale_entry, "裁剪尺寸比例")
        if not 0 < crop_scale <= 1:
            raise ValueError("裁剪尺寸比例必须在 0 和 1 之间")

        return ProcessingOptions(
            enhance=self.enhance_var.get(),
            rotate=self.rotate_var.get(),
            crop=self.crop_var.get(),
            brightness_factor=brightness,
            contrast_factor=contrast,
            center_number=center_number,
            fixed_angle=fixed_angle,
            spot_threshold=spot_threshold,
            line_threshold=line_threshold,
            crop_proportion=crop_proportion,
            crop_scale=crop_scale,
            draw_rotation_reference=self.draw_reference_var.get(),
        )

    @staticmethod
    def _read_float(entry: ttk.Entry, label: str) -> float:
        try:
            return float(entry.get().strip())
        except ValueError as exc:
            raise ValueError(f"{label}必须为数字") from exc

    @staticmethod
    def _read_int(entry: ttk.Entry, label: str) -> int:
        try:
            return int(entry.get().strip())
        except ValueError as exc:
            raise ValueError(f"{label}必须为整数") from exc

    def _run_processing(self, input_dir: str, output_dir: str, options: ProcessingOptions) -> None:
        try:
            process_folder(input_dir, output_dir, options, self._schedule_progress)
            self.root.after(10, self._finish_processing, "处理完成")
        except Exception as exc:
            self.root.after(10, self._show_error, str(exc))

    def _schedule_progress(self, result: ProcessingResult, index: int, total: int) -> None:
        progress = index / total * 100
        self.root.after(10, self._update_progress, result, progress)

    def _update_progress(self, result: ProcessingResult, progress_value: float) -> None:
        self.progress["value"] = progress_value
        self.progress_label.config(text=f"处理中: {int(progress_value)}%")
        status = "成功" if result.success else "失败"
        item_id = self.tree.insert("", "end", text=result.filename, values=(status, result.message))
        self.tree.see(item_id)

    def _finish_processing(self, message: str) -> None:
        self.processing = False
        self.process_btn.config(state=tk.NORMAL)
        self.progress_label.config(text=message)
        messagebox.showinfo("完成", message)

    def _show_error(self, message: str) -> None:
        self.processing = False
        self.process_btn.config(state=tk.NORMAL)
        self.progress_label.config(text="处理失败")
        messagebox.showerror("错误", message)


def main() -> None:
    root = tk.Tk()
    ImageProcessorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
