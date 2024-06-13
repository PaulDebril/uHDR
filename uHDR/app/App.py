# uHDR: HDR image editing software
#   Copyright (C) 2022  remi cozot 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
# hdrCore project 2020-2022
# author: remi.cozot@univ-littoral.fr

# import
# ------------------------------------------------------------------------------------------
from __future__ import annotations
import copy
from typing import Optional, Tuple, List, Dict

from numpy import ndarray
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QMainWindow, QApplication

import preferences.Prefs
from app.Jexif import Jexif
from app.ImageFIles import ImageFiles
from app.Tags import Tags
from app.SelectionMap import SelectionMap
from guiQt.MainWindow import MainWindow
from guiQt.LightBlock import LightBlock
from hdrCore import image as Image, processing

# ------------------------------------------------------------------------------------------
# --- class App ----------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
class App:
    def __init__(self: App) -> None:
        """uHDR v7 application"""
        # Load preferences
        preferences.Prefs.Prefs.load()

        # Initialize attributes
        self.original_image = None  
        self.modified_image = None  
        self.exposure_value = 0
        self.contrast_value = 0  
        self.saturation_value = 0  
        self.highlight_value = 90  
        self.shadows_value = 10 
        self.blacks_value = 30
        self.mediums_value = 50  
        self.whites_value = 70  
        self.color_selection: Dict[str, Tuple[int, int]] = {}
        self.editor_values: Dict[str, float] = {
            'hue shift': 0.0,
            'saturation': 0.0,
            'exposure': 0.0,
            'contrast': 0.0
        }
        self.lightness_mask_values: Dict[str, bool] = {
            'shadows': False,
            'blacks': False,
            'mediums': False,
            'whites': False,
            'highlights': False
        }
        self.show_mask = False

        # Initialize image management
        self.images_management: ImageFiles = ImageFiles()
        self.images_management.imageLoaded.connect(self.image_loaded_callback)
        self.images_management.setPrefs()
        self.images_management.checkExtra()
        nb_images: int = self.images_management.setDirectory(preferences.Prefs.Prefs.currentDir)

        # Initialize tags
        all_tags_in_dir: dict[str, dict[str, bool]] = Tags.aggregateTagsFiles(preferences.Prefs.Prefs.currentDir, preferences.Prefs.Prefs.extraPath)
        self.tags: Tags = Tags(Tags.aggregateTagsData([preferences.Prefs.Prefs.tags, all_tags_in_dir]))
        
        # Initialize selection map
        self.selection_map: SelectionMap = SelectionMap(self.images_management.getImagesFilesnames())
        self.selected_image_idx: int | None = None

        # Initialize main window
        self.main_window: MainWindow = MainWindow(nb_images, self.tags.toGUI())
        self.main_window.showMaximized()
        self.main_window.show()

        # Connect signals and slots
        self.connect_signals()

        # Set preferences
        self.main_window.setPrefs()

    def connect_signals(self):
        self.main_window.dirSelected.connect(self.directory_selected_callback)
        self.main_window.requestImages.connect(self.request_images_callback)
        self.main_window.imageSelected.connect(self.image_selected_callback)
        self.main_window.tagChanged.connect(self.tag_changed_callback)
        self.main_window.scoreChanged.connect(self.score_changed_callback)
        self.main_window.exposureChanged.connect(self.adjust_exposure)
        self.main_window.saturationChanged.connect(self.adjust_saturation)
        self.main_window.contrastChanged.connect(self.adjust_contrast)
        self.main_window.highlightChanged.connect(self.adjust_highlights)
        self.main_window.shadowsChanged.connect(self.adjust_shadows)
        self.main_window.blacksChanged.connect(self.adjust_blacks)
        self.main_window.mediumsChanged.connect(self.adjust_mediums)
        self.main_window.whitesChanged.connect(self.adjust_whites)
        self.main_window.selectionChanged.connect(self.on_selection_changed)
        self.main_window.editorValueChanged.connect(self.on_editor_value_changed)
        self.main_window.scoreSelectionChanged.connect(self.score_selection_changed_callback)
        self.main_window.showSelectionChanged.connect(self.on_show_selection_changed)
        self.main_window.lightnessMaskChanged.connect(self.on_lightness_mask_changed)

    def get_image_range_index(self: App) -> tuple[int, int]:
        """Return the index range (min index, max index) of images displayed by the gallery."""
        return self.main_window.imageGallery.getImageRangeIndex()

    def update_gallery(self: App) -> None:
        """Update gallery after selection changed or directory changed."""
        min_idx, max_idx = self.get_image_range_index()
        self.main_window.setNumberImages(self.selection_map.getSelectedImageNumber()) 
        self.main_window.setNumberImages(max_idx - min_idx) 
        self.request_images_callback(min_idx, max_idx)

    def directory_selected_callback(self: App, path: str) -> None:
        """Callback: called when directory is selected."""
        self.images_management.setDirectory(path)
        self.selection_map.setImageNames(self.images_management.getImagesFilesnames())
        self.selection_map.selectAll()
        self.main_window.resetGallery()
        self.main_window.setNumberImages(self.images_management.getNbImages())
        self.main_window.firstPage()

    def request_images_callback(self: App, min_idx: int, max_idx: int) -> None:
        """Callback: called when images are requested (occurs when page or zoom level is changed)."""
        image_filenames: list[str] = self.images_management.getImagesFilesnames()
        for s_idx in range(min_idx, max_idx + 1):
            g_idx: int | None = self.selection_map.selectedlIndexToGlobalIndex(s_idx) 
            if g_idx is not None:
                self.images_management.requestLoad(image_filenames[g_idx])
            else:
                self.main_window.setGalleryImage(s_idx, None)

    def image_loaded_callback(self: App, filename: str):
        """Callback: called when requested image is loaded (asynchronous loading)."""
        image: ndarray = self.images_management.images[filename]
        image_idx = self.selection_map.imageNameToSelectedIndex(filename)         
        if image_idx is not None:
            self.main_window.setGalleryImage(image_idx, image)

    def image_selected_callback(self: App, index):
        self.selected_image_idx = index
        g_idx: int | None = self.selection_map.selectedlIndexToGlobalIndex(index)
        if g_idx is not None:
            img: ndarray = self.images_management.getImage(self.images_management.getImagesFilesnames()[g_idx])
            tags: Tags = self.images_management.getImageTags(self.images_management.getImagesFilesnames()[g_idx])
            exif: dict[str, str] = self.images_management.getImageExif(self.images_management.getImagesFilesnames()[g_idx])
            score: int = self.images_management.getImageScore(self.images_management.getImagesFilesnames()[g_idx])
            self.main_window.setEditorImage(img)
            image_filename: str = self.images_management.getImagesFilesnames()[g_idx] 
            image_path: str = self.images_management.imagePath 
            self.main_window.setInfo(image_filename, image_path, *Jexif.toTuple(exif))
            self.main_window.setScore(score)
            self.main_window.resetTags()
            if tags:
                self.main_window.setTagsImage(tags.toGUI())

            # Reset original and modified images
            self.original_image = Image.Image(self.images_management.imagePath, self.images_management.getImagesFilesnames()[g_idx], img, Image.imageType.SDR, False, Image.ColorSpace.sRGB())
            self.modified_image = copy.deepcopy(self.original_image)
            self.apply_all_adjustments()

    def tag_changed_callback(self: App, key: tuple[str, str], value: bool) -> None:
        if self.selected_image_idx is not None:
            image_name: str | None = self.selection_map.selectedIndexToImageName(self.selected_image_idx)
            if image_name is not None:
                self.images_management.updateImageTag(image_name, key[0], key[1], value)

    def score_changed_callback(self: App, value: int) -> None:
        if self.selected_image_idx is not None:
            image_name: str | None = self.selection_map.selectedIndexToImageName(self.selected_image_idx)
            if image_name is not None:
                self.images_management.updateImageScore(image_name, value)

    def score_selection_changed_callback(self: App, list_selected_score: list[bool]) -> None:
        """Called when selection changed."""
        image_scores: dict[str, int] = self.images_management.imageScore
        selected_scores: list[int] = [i for i, selected in enumerate(list_selected_score) if selected]
        self.selection_map.selectByScore(image_scores, selected_scores)
        self.update_gallery()

    def adjust_exposure(self, ev_value):
        self.exposure_value = ev_value
        self.apply_all_adjustments()

    def adjust_contrast(self, value):
        self.contrast_value = value
        self.apply_all_adjustments()

    def adjust_saturation(self, value):
        self.saturation_value = value
        self.apply_all_adjustments()
        
    def on_editor_value_changed(self, values: dict) -> None:
        self.editor_values.update(values)
        self.apply_all_adjustments()
        
    def on_lightness_mask_changed(self, mask: dict) -> None:
        self.lightness_mask_values.update(mask)
        self.apply_all_adjustments()
        
    def on_show_selection_changed(self, show: bool) -> None:
        self.show_mask = show
        self.apply_all_adjustments()

    def apply_all_adjustments(self):
        if self.modified_image is None:
            return

        # Start from the original image
        self.modified_image = copy.deepcopy(self.original_image)

        # Apply exposure adjustment
        self.modified_image = processing.exposure().compute(self.modified_image, EV=self.exposure_value)

        # Apply contrast adjustment
        self.modified_image = processing.contrast().compute(self.modified_image, contrast=self.contrast_value)

        # Apply saturation adjustment
        self.modified_image = processing.saturation().compute(self.modified_image, saturation=self.saturation_value)
        
        # Apply lightness mask
        lightness_mask_params = {
            'shadows': self.lightness_mask_values.get('shadows', False),
            'blacks': self.lightness_mask_values.get('blacks', False),
            'mediums': self.lightness_mask_values.get('mediums', False),
            'whites': self.lightness_mask_values.get('whites', False),
            'highlights': self.lightness_mask_values.get('highlights', False),
        }
        self.modified_image = processing.lightnessMask().compute(self.modified_image, **lightness_mask_params)

        # Apply highlights adjustment
        highlights_params = {
            'start': [0, 0],
            'shadows': [10, self.shadows_value],
            'blacks': [30, self.blacks_value],
            'mediums': [50, self.mediums_value],
            'whites': [70, self.whites_value],
            'highlights': [90, self.highlight_value],
            'end': [100, 100]
        }
        self.modified_image = processing.Ycurve().compute(self.modified_image, **highlights_params)

        # Apply color editor adjustments
        color_params = {
            'selection': self.color_selection,
            'edit': {
                'hue': self.editor_values['hue shift'],
                'exposure': self.editor_values['exposure'],
                'contrast': self.editor_values['contrast'],
                'saturation': self.editor_values['saturation']
            },
            'tolerance': 0.1,
            'mask': self.show_mask,
        }
        self.modified_image = processing.colorEditor().compute(self.modified_image, **color_params)

        # Update the image in the user interface
        if isinstance(self.modified_image, Image.Image):
            image_name = self.selection_map.selectedIndexToImageName(self.selected_image_idx)
            if image_name:
                self.images_management.images[image_name] = self.modified_image.colorData
                self.main_window.setEditorImage(self.modified_image.colorData)
        else:
            print(f"Unexpected processed image type: {type(self.modified_image)}")

    def adjust_highlights(self, value: float) -> None:
        self.highlight_value = value
        self.apply_all_adjustments()
            
    def adjust_shadows(self, value: float) -> None:
        self.shadows_value = value
        self.apply_all_adjustments()
        
    def adjust_blacks(self, value: float) -> None:
        self.blacks_value = value
        self.apply_all_adjustments()
        
    def adjust_mediums(self, value: float) -> None:
        self.mediums_value = value
        self.apply_all_adjustments()
        
    def adjust_whites(self, value: float) -> None:
        self.whites_value = value
        self.apply_all_adjustments()

    def on_selection_changed(self, selection: Dict[str, Tuple[int, int]]) -> None:
        self.color_selection = selection
        self.apply_all_adjustments()
