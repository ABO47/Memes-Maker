import os
import sys
import logging
from PIL import Image, ImageDraw, ImageFont
import imageio
from moviepy import VideoFileClip
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QMessageBox, QGridLayout, QSpinBox, QGroupBox, QRadioButton,
    QComboBox, QColorDialog, QTextEdit
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon, QDesktopServices, QColor

class MediaCaptionAdder(QMainWindow):
    def __init__(self):
        super().__init__()
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
        self.font_path = self._get_default_font()
        self.setWindowTitle("Memes maker")
        self.setGeometry(100, 100, 500, 400)
        self.setup_ui()

    def _get_default_font(self) -> str:
        possible_fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/Library/Fonts/Arial.ttf",
            "C:\\Windows\\Fonts\\arial.ttf"
        ]
        for font_path in possible_fonts:
            if os.path.exists(font_path):
                return font_path
        return None

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        input_group = QGroupBox("Input Settings")
        input_layout = QGridLayout()

        self.file_path_label = QLabel("File Path:")
        self.file_path_entry = QLineEdit()
        self.file_path_button = QPushButton("Browse")
        self.file_path_button.clicked.connect(self.select_file)
        input_layout.addWidget(self.file_path_label, 0, 0)
        input_layout.addWidget(self.file_path_entry, 0, 1, 1, 2)
        input_layout.addWidget(self.file_path_button, 0, 3)

        self.caption_label = QLabel("Caption:")
        self.caption_entry = QTextEdit()
        self.caption_entry.setPlaceholderText("Enter your meme caption here...")
        self.caption_entry.setMaximumHeight(100)  # Limit height while allowing multiple lines
        input_layout.addWidget(self.caption_label, 1, 0)
        input_layout.addWidget(self.caption_entry, 1, 1, 1, 3)

        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        options_group = QGroupBox("Customization Options")
        options_layout = QGridLayout()

        self.font_size_label = QLabel("Font Size:")
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(10, 100)
        self.font_size_spinbox.setValue(30)
        options_layout.addWidget(self.font_size_label, 0, 0)
        options_layout.addWidget(self.font_size_spinbox, 0, 1)

        self.padding_label = QLabel("Padding:")
        self.padding_spinbox = QSpinBox()
        self.padding_spinbox.setRange(5, 50)
        self.padding_spinbox.setValue(10)
        options_layout.addWidget(self.padding_label, 1, 0)
        options_layout.addWidget(self.padding_spinbox, 1, 1)

        self.width_label = QLabel("Output Width:")
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(100, 2000)
        self.width_spinbox.setValue(800)
        options_layout.addWidget(self.width_label, 2, 0)
        options_layout.addWidget(self.width_spinbox, 2, 1)

        self.position_label = QLabel("Caption Position:")
        self.position_combo = QComboBox()
        self.position_combo.addItems(["Top", "Bottom"])
        options_layout.addWidget(self.position_label, 3, 0)
        options_layout.addWidget(self.position_combo, 3, 1)

        self.bg_color_label = QLabel("Background Color:")
        self.bg_color_button = QPushButton("Choose Color")
        self.bg_color_button.clicked.connect(self.choose_background_color)
        self.background_color = QColor(255, 255, 255)
        options_layout.addWidget(self.bg_color_label, 4, 0)
        options_layout.addWidget(self.bg_color_button, 4, 1)

        self.media_type_label = QLabel("Media Type:")
        media_type_layout = QHBoxLayout()
        self.gif_radio = QRadioButton("GIF")
        self.video_radio = QRadioButton("Video")
        self.image_radio = QRadioButton("Image")
        self.gif_radio.setChecked(True)

        media_type_layout.addWidget(self.media_type_label)
        media_type_layout.addWidget(self.gif_radio)
        media_type_layout.addWidget(self.video_radio)
        media_type_layout.addWidget(self.image_radio)
        media_type_layout.addStretch(1)

        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)

        media_type_widget = QWidget()
        media_type_widget.setLayout(media_type_layout)
        main_layout.addWidget(media_type_widget)

        process_button = QPushButton("Add the Caption")
        process_button.setStyleSheet("background-color: #525252; color: white;")
        process_button.clicked.connect(self.process_media)
        main_layout.addWidget(process_button, alignment=Qt.AlignmentFlag.AlignCenter)

        central_widget.setLayout(main_layout)

    def choose_background_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.background_color = color
            self.bg_color_button.setStyleSheet(f"background-color: {color.name()}")

    def select_file(self):
        file_types = "All Media Files (*.gif *.mp4 *.avi *.png *.jpg *.jpeg);;GIF Files (*.gif);;Video Files (*.mp4 *.avi);;Image Files (*.png *.jpg *.jpeg)"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Media File", "", file_types
        )
        if file_path:
            self.file_path_entry.setText(file_path)

    def _validate_inputs(self) -> bool:
        file_path = self.file_path_entry.text().strip()
        caption_text = self.caption_entry.toPlainText().strip()

        if not file_path:
            QMessageBox.warning(self, "Missing Input", "Please select a file.")
            return False

        if not caption_text:
            QMessageBox.warning(self, "Missing Input", "Please enter a caption.")
            return False

        return True

    def process_media(self):
        try:
            if not self._validate_inputs():
                return

            file_path = self.file_path_entry.text().strip()
            caption_text = self.caption_entry.toPlainText().strip()
            font_size = self.font_size_spinbox.value()
            padding = self.padding_spinbox.value()
            output_width = self.width_spinbox.value()
            position = self.position_combo.currentText()
            bg_color = (
                self.background_color.red(),
                self.background_color.green(),
                self.background_color.blue()
            )

            if self.gif_radio.isChecked():
                output_path = self.add_caption_to_gif(
                    file_path, caption_text, font_size, padding,
                    output_width, position, bg_color
                )
            elif self.video_radio.isChecked():
                output_path = self.add_caption_to_video(
                    file_path, caption_text, font_size, padding,
                    output_width, position, bg_color
                )
            elif self.image_radio.isChecked():
                output_path = self.add_caption_to_image(
                    file_path, caption_text, font_size, padding,
                    output_width, position, bg_color
                )

            self.open_file(output_path)
            QMessageBox.information(self, "Success", f"Media saved at: {output_path}")
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
            QMessageBox.critical(self, "Error", "Selected file could not be found.")
        except PermissionError:
            logging.error(f"Permission denied accessing: {file_path}")
            QMessageBox.critical(self, "Error", "Permission denied. Cannot access the file.")
        except Exception as e:
            logging.error(f"Unexpected error in media processing: {e}")
            QMessageBox.critical(self, "Unexpected Error", str(e))

    def add_caption_to_image(self, image_path, caption_text, font_size,
                              padding, output_width, position, bg_color):
        font_path = self.font_path or "arial.ttf"
        os.makedirs(os.path.join(os.getcwd(), "output"), exist_ok=True)

        try:
            pil_image = Image.open(image_path).convert("RGBA")
            media_height = int(output_width * pil_image.height / pil_image.width)
            pil_image = pil_image.resize((output_width, media_height))

            font = ImageFont.truetype(font_path, font_size)
            draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))

            wrapped_text = self._wrap_text(caption_text, font, output_width - 2 * padding)
            text_bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
            text_height = text_bbox[3] - text_bbox[1]

            caption_block_height = text_height + 2 * padding
            total_height = media_height + caption_block_height if position == "Top" else media_height

            canvas = Image.new("RGBA", (output_width, total_height), color=bg_color)
            draw = ImageDraw.Draw(canvas)

            caption_y = 0 if position == "Top" else total_height - caption_block_height
            image_y = caption_block_height if position == "Top" else 0

            draw.rectangle(
                (0, caption_y, output_width, caption_y + caption_block_height),
                fill=bg_color
            )
            draw.multiline_text(
                (padding, caption_y + padding),
                wrapped_text, fill="black", font=font, align="left"
            )

            canvas.paste(pil_image, (0, image_y))

            output_path = os.path.join(os.getcwd(), "output", "output.png")
            canvas.save(output_path)
            return output_path
        except OSError:
            logging.error(f"Could not load font: {font_path}")
            font = ImageFont.load_default()

    def add_caption_to_video(self, video_path, caption_text, font_size,
                              padding, output_width, position, bg_color):
        font_path = self.font_path or "arial.ttf"
        clip = VideoFileClip(video_path)
        new_height = int(output_width * clip.h / clip.w)

        font = ImageFont.truetype(font_path, font_size)
        draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))

        wrapped_text = self._wrap_text(caption_text, font, output_width - 2 * padding)
        text_bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
        text_height = text_bbox[3] - text_bbox[1]

        caption_block_height = text_height + 2 * padding
        total_height = new_height + caption_block_height if position == "Top" else new_height

        def caption_overlay(get_frame, t):
            frame = get_frame(t)
            pil_image = Image.fromarray(frame).resize((output_width, new_height))
            canvas = Image.new("RGBA", (output_width, total_height), color=bg_color)
            draw = ImageDraw.Draw(canvas)

            caption_y = 0 if position == "Top" else total_height - caption_block_height
            image_y = caption_block_height if position == "Top" else 0

            draw.rectangle(
                (0, caption_y, output_width, caption_y + caption_block_height),
                fill=bg_color
            )
            draw.multiline_text(
                (padding, caption_y + padding),
                wrapped_text, fill="black", font=font, align="left"
            )

            canvas.paste(pil_image, (0, image_y))
            return canvas

        final_clip = clip.fl(caption_overlay).resize(width=output_width)
        output_path = os.path.join(os.getcwd(), "output", "output.mp4")
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        return output_path

    def add_caption_to_gif(self, gif_path, caption_text, font_size,
                            padding, output_width, position, bg_color):
        font_path = self.font_path or "arial.ttf"
        gif = imageio.mimread(gif_path)
        edited_frames = []

        font = ImageFont.truetype(font_path, font_size)
        draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))

        wrapped_text = self._wrap_text(caption_text, font, output_width - 2 * padding)
        text_bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
        text_height = text_bbox[3] - text_bbox[1]

        caption_block_height = text_height + 2 * padding

        for frame in gif:
            pil_image = Image.fromarray(frame)
            media_height = int(output_width * pil_image.height / pil_image.width)
            total_height = media_height + caption_block_height if position == "Top" else media_height

            canvas = Image.new("RGBA", (output_width, total_height), color=bg_color)
            draw = ImageDraw.Draw(canvas)

            resized_image = pil_image.resize((output_width, media_height))

            caption_y = 0 if position == "Top" else total_height - caption_block_height
            image_y = caption_block_height if position == "Top" else 0

            draw.rectangle(
                (0, caption_y, output_width, caption_y + caption_block_height),
                fill=bg_color
            )
            draw.multiline_text(
                (padding, caption_y + padding),
                wrapped_text, fill="black", font=font, align="left"
            )

            canvas.paste(resized_image, (0, image_y))
            edited_frames.append(canvas)

        output_path = os.path.join(os.getcwd(), "output", "output.gif")
        os.makedirs(os.path.join(os.getcwd(), "output"), exist_ok=True)
        edited_frames[0].save(
            output_path,
            save_all=True,
            append_images=edited_frames[1:],
            loop=0,
            duration=100,
        )
        return output_path

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
        words = text.split(" ")
        if not words:
            return ""

        lines = []
        current_line = words[0]

        for word in words[1:]:
            test_line = current_line + " " + word
            test_bbox = font.getbbox(test_line)
            test_width = test_bbox[2] - test_bbox[0]

            if test_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)
        return "\n".join(lines)

    def open_file(self, file_path):
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not open file: {e}")


def main():
    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")

        window = MediaCaptionAdder()
        window.setWindowTitle("Meme Maker")

        icon_path = "path/to/icon.png"
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            window.setWindowIcon(icon)

        window.show()
        sys.exit(app.exec())

    except Exception as e:
        logging.critical(f"Critical application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()