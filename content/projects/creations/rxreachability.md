{
  "title": "RxReachability",
  "date": "2018-02-11T12:41:05-05:00",
  "image": "/img/circleci-workflow.png",
  "link": "https://github.com/rxswiftcommunity/rxreachability",
  "image": "https://raw.githubusercontent.com/RxSwiftCommunity/RxReachability/master/Assets/Logo.png",
  "description": "RxReachability adds easy to use RxSwift bindings for ReachabilitySwift. You can react to network reachability changes and even retry observables when network comes back up.",
  "tags": ["Swift", "Objective-C", "macOS", "iOS", "tvOS", "MVVM", "Rx", "Realm"],
  "fact": "",
  "featured":true,
  "weight": 2
}

[RxReachability](https://github.com/rxswiftcommunity/rxreachability) is an open source project that I voluneteered to take ownership of in 2019.

It's a small but vital project to many apps in the iOS community for providing a simple RxSwift bindable interface for use in funciontal code dependendant on network connectivity state.

This project is also served as a [Cocoapod](https://cocoapods.org/pods/Reachability), the publishing of which is automated through GitHub actions I authored along with a suite of other CI/CD tools to assist with administrating such an important open-source project.

This project also support SwiftPM and Carthage.

---

![Logo](https://raw.githubusercontent.com/RxSwiftCommunity/RxReachability/master/Assets/Logo.png)

RxReachability
=========
[![GitHub release](https://img.shields.io/github/release/RxSwiftCommunity/rxreachability.svg)](https://github.com/RxSwiftCommunity/rxreachability/releases)
[![Version](https://img.shields.io/cocoapods/v/RxReachability.svg?style=flat)](http://cocoapods.org/pods/RxReachability)
[![License](https://img.shields.io/cocoapods/l/RxReachability.svg?style=flat)](http://cocoapods.org/pods/RxReachability)
[![Platform](https://img.shields.io/cocoapods/p/RxReachability.svg?style=flat)](http://cocoapods.org/pods/RxReachability)
[![Build Status](https://travis-ci.org/RxSwiftCommunity/RxReachability.svg?branch=master)](https://travis-ci.org/RxSwiftCommunity/RxReachability)
![Test Coverage](https://raw.githubusercontent.com/RxSwiftCommunity/RxReachability/master/docs/badge.svg)

RxReachability adds easy to use RxSwift bindings for [ReachabilitySwift](https://github.com/ashleymills/Reachability.swift).
You can react to network reachability changes and even retry observables when network comes back up.

## Available APIs

RxReachability adds the following RxSwift bindings:

- `reachabilityChanged: Observable<Reachability>`
- `status: Observable<Reachability.NetworkStatus>`
- `isReachable: Observable<Bool>`
- `isConnected: Observable<Void>`
- `isDisconnected: Observable<Void>`

## Common Usage

#### 1. Be sure to store an instance of `Reachability` in your `ViewController` or similar, and start/stop the notifier on `viewWillAppear` and `viewWillDisappear` methods.

```swift
class ViewController: UIViewController {

  let disposeBag = DisposeBag()
  var reachability: Reachability?

  override func viewDidLoad() {
    super.viewDidLoad()
    reachability = Reachability()
  }

  override func viewWillAppear(_ animated: Bool) {
    super.viewWillAppear(animated)
    try? reachability?.startNotifier()
  }

  override func viewWillDisappear(_ animated: Bool) {
    super.viewWillDisappear(animated)
    reachability?.stopNotifier()
  }
}

```

#### 2. Subscribe to any of the bindings to know when a change happens.

```swift
extension ViewController {

  let disposeBag = DisposeBag()

  func bindReachability() {

    reachability?.rx.reachabilityChanged
      .subscribe(onNext: { reachability: Reachability in
        print("Reachability changed: \(reachability.currentReachabilityStatus)")
      })
      .disposed(by: disposeBag)

    reachability?.rx.status
      .subscribe(onNext: { status: Reachability.NetworkStatus in
        print("Reachability status changed: \(status)")
      })
      .disposed(by: disposeBag)

    reachability?.rx.isReachable
      .subscribe(onNext: { isReachable: Bool in
        print("Is reachable: \(isReachable)")
      })
      .disposed(by: disposeBag)

    reachability?.rx.isConnected
      .subscribe(onNext: {
        print("Is connected")
      })
      .disposed(by: disposeBag)

    reachability?.rx.isDisconnected
      .subscribe(onNext: {
        print("Is disconnected")
      })
      .disposed(by: disposeBag)
  }
```

## Static Usage

#### 1. Be sure to store an instance of `Reachability` somewhere on your `AppDelegate` or similar, and start the notifier.

```swift
import Reachability

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

  var reachability: Reachability?

  func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplicationLaunchOptionsKey: Any]?) -> Bool {
    reachability = Reachability()
    try? reachability?.startNotifier()
    return true
  }
}

```

#### 2. Subscribe to any of the bindings to know when a change happens.

```swift
import Reachability
import RxReachability
import RxSwift

class ViewController: UIViewController {

  let disposeBag = DisposeBag()

  override func viewDidLoad() {
    super.viewDidLoad()

    Reachability.rx.reachabilityChanged
      .subscribe(onNext: { reachability: Reachability in
        print("Reachability changed: \(reachability.currrentReachabilityStatus)")
      })
      .disposed(by: disposeBag)

    Reachability.rx.status
      .subscribe(onNext: { status: Reachability.NetworkStatus in
        print("Reachability status changed: \(status)")
      })
      .disposed(by: disposeBag)

    Reachability.rx.isReachable
      .subscribe(onNext: { isReachable: Bool in
        print("Is reachable: \(isReachable)")
      })
      .disposed(by: disposeBag)

    Reachability.rx.isConnected
      .subscribe(onNext: {
        print("Is connected")
      })
      .disposed(by: disposeBag)

    Reachability.rx.isDisconnected
      .subscribe(onNext: {
        print("Is disconnected")
      })
      .disposed(by: disposeBag)
  }
```

## Advanced Usage

With RxReachability you can also add a retry when network comes back up with a given timeout.
This does require you to have a stored instance of Reachability though.

```swift
func request(somethingId: Int) -> Observable<Something> {
  return network.request(.something(somethingId))
    .retryOnConnect(timeout: 30)
    .map { Something(JSON: $0) }
}
```

## Installation

### Installation via CocoaPods

To integrate RxReachability into your Xcode project using CocoaPods, simply add the following line to your `Podfile`:

```ruby
pod 'RxReachability', ~> '1.2.1'
```

### Installation via Carthage

To integrate RxReachability into your Xcode project using CocoaPods, simply add the following line to your `Cartfile`:

```ruby
github RxSwiftCommunity/RxReachability ~> 1.2.1
```

### Installation via Swift Package Manager (SPM)

To integrate RxReachability into your Xcode project using SPM, simply add the following line to your `Package.swift`:

```swift
.package(url: "https://github.com/RxSwiftCommunity/RxReachability", .upToNextMajor(from: "1.2.1")),
```

## Example

To run the example project, clone the repo, and run `pod install` from the Example directory first.

## License

This library belongs to _RxSwiftCommunity_.

RxReachability is available under the MIT license. See the LICENSE file for more info.
{"mode":"full","isActive":false}