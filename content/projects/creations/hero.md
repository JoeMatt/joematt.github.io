{
  "title": "Hero",
  "date": "2018-02-11T12:41:05-05:00",
  "image": "/img/circleci-workflow.png",
  "link": "https://github.com/HeroTransitions/Hero",
  "image": "https://cdn.rawgit.com/lkzhao/Hero/427d5f2/Resources/Hero.svg",
  "description": "Hero is a library for building iOS view controller transitions. It provides a declarative layer on top of the UIKit's cumbersome transition APIs—making custom transitions an easy task for developers.",
  "tags": ["Swift", "Objective-C", "AArch64", "iOS", "tvOS"],
  "fact": "",
  "featured":true,
  "weight": 2
}

[Hero Transitions](https://github.com/HeroTransitions/Hero) is an open source project that I voluneteered to take ownership of in 2019.

This project is also served as a [Cocoapod](https://cocoapods.org/pods/Hero), the publishing of which is automated through GitHub actions I authored along with a suite of other CI/CD tools to assist with administrating such an important open-source project.

This project also support SwiftPM and Carthage.

---

<img src="https://cdn.rawgit.com/lkzhao/Hero/427d5f2/Resources/Hero.svg" width="388"/>

**Hero** is a library for building iOS view controller transitions. It provides a declarative layer on top of the UIKit's cumbersome transition APIs—making custom transitions an easy task for developers.

[![Carthage compatible](https://img.shields.io/badge/Carthage-Compatible-brightgreen.svg?style=flat)](https://github.com/Carthage/Carthage)
[![Accio supported](https://img.shields.io/badge/Accio-supported-0A7CF5.svg?style=flat)](https://github.com/JamitLabs/Accio)
[![codecov](https://codecov.io/gh/HeroTransitions/Hero/branch/develop/graph/badge.svg)](https://codecov.io/gh/HeroTransitions/Hero)
[![Version](https://img.shields.io/cocoapods/v/Hero.svg?style=flat)](http://cocoapods.org/pods/Hero)
[![License](https://img.shields.io/cocoapods/l/Hero.svg?style=flat)](https://github.com/lkzhao/Hero/blob/master/LICENSE?raw=true)
![Xcode 9.0+](https://img.shields.io/badge/Xcode-9.0%2B-blue.svg)
![iOS 8.0+](https://img.shields.io/badge/iOS-8.0%2B-blue.svg)
![Swift 4.0+](https://img.shields.io/badge/Swift-4.0%2B-orange.svg)
[![中文 README](https://img.shields.io/badge/%E4%B8%AD%E6%96%87-README-blue.svg?style=flat)](https://github.com/lkzhao/Hero/blob/master/README.zh-cn.md)
[![Donate](https://img.shields.io/badge/Donate-PayPal-blue.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=NT5F7Y2MPV7RE)

<img src="https://cdn.rawgit.com/lkzhao/Hero/ebb3f2c/Resources/features.svg"/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://cdn.rawgit.com/lkzhao/Hero/ebb3f2c/Resources/features2.svg"/>

Hero is similar to Keynote's **Magic Move**. It checks the `heroID` property on all source and destination views. Every matched view pair is then automatically transitioned from its old state to its new state.

Hero can also construct animations for unmatched views. It is easy to define these animations via the `heroModifiers` property. Hero will run these animations alongside the **Magic Move** animations. All of these animations can be **interactively controlled** by user gestures.

At view controller level, Hero provides several template transitions that you can set through `heroModalAnimationType`, `heroNavigationAnimationType`, and `heroTabBarAnimationType`. These can be used as the foundation of your custom transitions. Combine with `heroID` & `heroModifiers` to make your own unique transitions.

<img src="https://cdn.rawgit.com/lkzhao/Hero/ebb3f2c/Resources/defaultAnimations.svg"/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://cdn.rawgit.com/lkzhao/Hero/ebb3f2c/Resources/defaultAnimations2.svg"/>

By default, Hero provides **dynamic duration** based on the [Material Design Motion Guide](https://material.io/design/motion/speed.html#easing). Duration is automatically determined by changes to distance and size—saving you the hassle, while providing consistent and delightful animations.

Hero doesn't make any assumptions about how the view is built or structured. It won't modify any of your views' states other than hiding them during the animation. This makes it work with **Auto Layout**, **programmatic layout**, **UICollectionView** (without modifying its layout object), **UITableView**, **UINavigationController**, **UITabBarController**, etc...

## Usage Example 1

<img src="https://cdn.rawgit.com/lkzhao/Hero/ebb3f2c/Resources/simple.svg" />

### View Controller 1

```swift
redView.hero.id = "ironMan"
blackView.hero.id = "batMan"
```

### View Controller 2

```swift
self.hero.isEnabled = true
redView.hero.id = "ironMan"
blackView.hero.id = "batMan"
whiteView.hero.modifiers = [.translate(y:100)]
```

## Usage Example 2

<img src="https://cdn.rawgit.com/lkzhao/Hero/ebb3f2c/Resources/advanced.svg" />

### View Controller 1

```swift
greyView.hero.id = "skyWalker"
```

### View Controller 2

```swift
self.hero.isEnabled = true
greyView.hero.id = "skyWalker"

// collectionView is the parent view of all red cells
collectionView.hero.modifiers = [.cascade]
for cell in redCells {
    cell.hero.modifiers = [.fade, .scale(0.5)]
}
```

You can do these in the **storyboard** too!

<img src="https://cdn.rawgit.com/lkzhao/Hero/master/Resources/storyboardView.png" width="267px"/> 
<img src="https://cdn.rawgit.com/lkzhao/Hero/master/Resources/storyboardViewController.png" width="267px"/>

## Installation

### CocoaPods

Add the following entry to your Podfile:

```rb
pod 'Hero'
```

Then run `pod install`.

Don't forget to `import Hero` in every file you'd like to use Hero.

### Carthage

Add the following entry to your `Cartfile`:

```text
github "HeroTransitions/Hero"
```

Then run `carthage update`.

If this is your first time using Carthage in the project, you'll need to go through some additional steps as explained [over at Carthage](https://github.com/Carthage/Carthage#adding-frameworks-to-an-application).

### Accio

Add the following to your `Package.swift`:

```swift
.package(url: "https://github.com/HeroTransitions/Hero.git", .upToNextMajor(from: "1.4.0")),
```

Next, add `Hero` to your App targets dependencies like so:

```swift
.target(
    name: "App",
    dependencies: [
        "Hero",
    ]
),
```

Then run `accio update`.

### Swift Package Manager

To integrate using Apple's Swift package manager, add the following as a dependency to your `Package.swift`:

```swift
.package(url: "https://github.com/HeroTransitions/Hero.git", .upToNextMajor(from: "1.3.0"))
```

and then specify `"Hero"` as a dependency of the Target in which you wish to use Hero.
Here's an example `PackageDescription`:

```swift
// swift-tools-version:4.0
import PackageDescription

let package = Package(
    name: "MyPackage",
    products: [
        .library(
            name: "MyPackage",
            targets: ["MyPackage"]),
    ],
    dependencies: [
        .package(url: "https://github.com/HeroTransitions/Hero.git", .upToNextMajor(from: "1.6.1"))
    ],
    targets: [
        .target(
            name: "MyPackage",1.6.1
            dependencies: ["Hero"])
    ]
)
```

### Manually

- Drag the **Sources** folder anywhere in your project.

## Documentations

Checkout the **[WIKI PAGES (Usage Guide)](https://github.com/lkzhao/Hero/wiki/Usage-Guide)** for documentations.

For more up-to-date ones, please see the header-doc. (use **alt+click** in Xcode)
<img src="https://cdn.rawgit.com/lkzhao/Hero/master/Resources/headerDoc.png" width="521px"/>

## Interactive Transition Tutorials

[Interactive transitions with Hero (Part 1)](https://lkzhao.gitbooks.io/hero/content/docs/InteractiveTransition.html)

## FAQ

### Not able to use Hero transition even when `self.hero.isEnabled` is set to true

Make sure that you have also enabled `self.hero.isEnabled` on the navigation controller if you are doing a push/pop inside the navigation controller.

### Views being covered by another matched view during the transition

Matched views use global coordinate space while unmatched views use local coordinate space by default. Local coordinate spaced views might be covered by other global coordinate spaced views. To solve this, use the `useGlobalCoordinateSpace` modifier on the views being covered. Checkout [Coordinate Space Wiki page](https://github.com/lkzhao/Hero/wiki/Coordinate-Space) for details.

### Push animation is shown along side my custom animation

This is the default animation for navigation controller provided by Hero. To disable the push animation, set `self.hero.navigationAnimationType` to `.fade` or `.none` on the navigation controller.

### How do I use a different default animation when dismissing

You can use the animation type `.selectBy(presenting:dismissing)` to specify a different default animation for dismiss.

For example:

```swift
    self.hero.modalAnimationType = .selectBy(presenting:.zoom, dismissing:.zoomOut)
```

## Contribute

We welcome any contributions. Please read the [Contribution Guide](https://github.com/lkzhao/Hero/wiki/Contribution-Guide).
{"mode":"full","isActive":false}