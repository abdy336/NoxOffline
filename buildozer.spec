[app]
title = NoxPlayer Offline
package.name = noxoffline
package.domain = org.abdy.edits
source.dir = .
source.include_exts = py,png,jpg,jpeg,json
version = 0.1
requirements = python3,kivy,pillow
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0
python_for_android_url = https://github.com/kivy/python-for-android
python_for_android_branch = master

[buildozer]
log_level = 2
warn_on_root = 1
