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

from numpy import ndarray
from app.Jexif import Jexif

import preferences.Prefs
from guiQt.MainWindow import MainWindow
from app.ImageFIles import ImageFiles
from app.Tags import Tags
from app.SelectionMap import SelectionMap
from guiQt.LightBlock import LightBlock
from hdrCore.processing import exposure
from hdrCore import image, processing

from PyQt6.QtWidgets import QVBoxLayout, QWidget, QMainWindow, QApplication

# ------------------------------------------------------------------------------------------
# --- class App ----------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
debug : bool = True
class App:
    # static attributes

    # constructor
    def __init__(self: App) -> None:
        """uHDR v7 application"""
        # loading preferences
        preferences.Prefs.Prefs.load()
        self.original_image = None  # Ajouter une variable pour stocker l'image originale

        self.imagesManagement: ImageFiles = ImageFiles()
        self.imagesManagement.imageLoaded.connect(self.CBimageLoaded)
        self.imagesManagement.setPrefs()
        self.imagesManagement.checkExtra()
        nbImages: int = self.imagesManagement.setDirectory(preferences.Prefs.Prefs.currentDir)

        allTagsInDir: dict[str, dict[str, bool]] = Tags.aggregateTagsFiles(preferences.Prefs.Prefs.currentDir, preferences.Prefs.Prefs.extraPath)
        self.tags: Tags = Tags(Tags.aggregateTagsData([preferences.Prefs.Prefs.tags, allTagsInDir]))
        
        self.selectionMap: SelectionMap = SelectionMap(self.imagesManagement.getImagesFilesnames())
        self.selectedImageIdx: int | None = None

        self.mainWindow: MainWindow = MainWindow(nbImages, self.tags.toGUI())
        self.mainWindow.showMaximized()
        self.mainWindow.show()

        self.mainWindow.dirSelected.connect(self.CBdirSelected)
        self.mainWindow.requestImages.connect(self.CBrequestImages)
        self.mainWindow.imageSelected.connect(self.CBimageSelected)

        self.mainWindow.tagChanged.connect(self.CBtagChanged)
        self.mainWindow.scoreChanged.connect(self.CBscoreChanged)
        self.mainWindow.exposureChanged.connect(self.adjustExposure)

        self.mainWindow.scoreSelectionChanged.connect(self.CBscoreSelectionChanged)

        self.mainWindow.setPrefs()

    def getImageRangeIndex(self: App) -> tuple[int, int]:
        """return the index range (min index, max index) of images displayed by the gallery."""
        return self.mainWindow.imageGallery.getImageRangeIndex()

    def update(self: App) -> None:
        """call to update gallery after selection changed or directory changed."""
        minIdx, maxIdx = self.getImageRangeIndex()
        self.mainWindow.setNumberImages(self.selectionMap.getSelectedImageNumber()) 
        self.mainWindow.setNumberImages(maxIdx - minIdx) 
        self.CBrequestImages(minIdx, maxIdx)

    def CBdirSelected(self: App, path: str) -> None:
        """callback: called when directory is selected."""
        if debug: 
            print(f'App.CBdirSelected({path})')
        self.imagesManagement.setDirectory(path)
        self.selectionMap.setImageNames(self.imagesManagement.getImagesFilesnames())
        self.selectionMap.selectAll()
        self.mainWindow.resetGallery()
        self.mainWindow.setNumberImages(self.imagesManagement.getNbImages())
        self.mainWindow.firstPage()

    def CBrequestImages(self: App, minIdx: int, maxIdx: int) -> None:
        """callback: called when images are requested (occurs when page or zoom level is changed)."""
        imagesFilenames: list[str] = self.imagesManagement.getImagesFilesnames()
        for sIdx in range(minIdx, maxIdx+1):
            gIdx: int | None = self.selectionMap.selectedlIndexToGlobalIndex(sIdx) 
            if gIdx is not None:
                self.imagesManagement.requestLoad(imagesFilenames[gIdx])
            else:
                self.mainWindow.setGalleryImage(sIdx, None)

    def CBimageLoaded(self: App, filename: str):
        """"callback: called when requested image is loaded (asynchronous loading)."""
        image: ndarray = self.imagesManagement.images[filename]
        imageIdx = self.selectionMap.imageNameToSelectedIndex(filename)         
        if imageIdx is not None:
            self.mainWindow.setGalleryImage(imageIdx, image)

    def CBimageSelected(self: App, index):
        self.selectedImageIdx = index
        gIdx: int | None = self.selectionMap.selectedlIndexToGlobalIndex(index)
        if gIdx is not None:
            image: ndarray = self.imagesManagement.getImage(self.imagesManagement.getImagesFilesnames()[gIdx])
            tags: Tags = self.imagesManagement.getImageTags(self.imagesManagement.getImagesFilesnames()[gIdx])
            exif: dict[str, str] = self.imagesManagement.getImageExif(self.imagesManagement.getImagesFilesnames()[gIdx])
            score: int = self.imagesManagement.getImageScore(self.imagesManagement.getImagesFilesnames()[gIdx])
            self.mainWindow.setEditorImage(image)
            imageFilename: str = self.imagesManagement.getImagesFilesnames()[gIdx] 
            imagePath: str = self.imagesManagement.imagePath 
            self.mainWindow.setInfo(imageFilename, imagePath, *Jexif.toTuple(exif))
            self.mainWindow.setScore(score)
            self.mainWindow.resetTags()
            if tags:
                self.mainWindow.setTagsImage(tags.toGUI())

    def CBtagChanged(self: App, key: tuple[str, str], value: bool) -> None:
        if self.selectedImageIdx is not None:
            imageName: str | None = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if debug:
                print(f'\t\t imageName:{imageName}')
            if imageName is not None:
                self.imagesManagement.updateImageTag(imageName, key[0], key[1], value)
    
    def CBscoreChanged(self: App, value: int) -> None:
        if self.selectedImageIdx is not None:
            imageName: str | None = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if imageName is not None:
                self.imagesManagement.updateImageScore(imageName, value)

    def CBscoreSelectionChanged(self: App, listSelectedScore: list[bool]) -> None:
        """called when selection changed."""
        imageScores: dict[str, int] = self.imagesManagement.imageScore
        selectedScores: list[int] = []
        for i, selected in enumerate(listSelectedScore):
            if selected:
                selectedScores.append(i)
        self.selectionMap.selectByScore(imageScores, selectedScores)
        self.update()

    def adjustExposure(self, ev_value):
        print(f"adjustExposure called with ev_value: {ev_value}")
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            print(f"Selected image name: {imageName}")
            if imageName:
                # Si l'image originale n'a pas encore été copiée, faites-le maintenant
                if self.original_image is None:
                    img = self.imagesManagement.getImage(imageName)
                    # Vérifiez si l'image est une instance de hdrCore.image.Image
                    if not isinstance(img, image.Image):
                        # Si ce n'est pas le cas, convertissez-la en hdrCore.image.Image
                        img = image.Image(self.imagesManagement.imagePath, imageName, img, image.imageType.SDR, False, image.ColorSpace.sRGB())
                    self.original_image = img  # Stocker l'image originale

                # Créer une copie de l'image originale
                img = copy.deepcopy(self.original_image)

                exposure_processor = processing.exposure()
                processed_image = exposure_processor.compute(img, EV=ev_value)

                if isinstance(processed_image, image.Image):
                    self.imagesManagement.images[imageName] = processed_image.colorData  # Extraire les données de l'image
                    self.mainWindow.setEditorImage(processed_image.colorData)  # Extraire les données de l'image
                else:
                    print(f"Unexpected processed image type: {type(processed_image)}")