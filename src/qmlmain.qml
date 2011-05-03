import QtQuick 1.0
import QtWebKit 1.0
import "components" 

Rectangle {
    id: main
    width: 400
    height: 400
    opacity: 1
    state: "Books"

    function setURL(url) {
        console.log(url)
        webview.url = url
    }
    
    function setBookStoreModel(model) {
        bookstorecontents.model = model
    }

    function setContents(mod) {
        contents.model = mod
    }

    function setBookStorePage(url) {
        bookstorepage.url = url
    }

    Rectangle {
        id: actions
        height: 65
        width: parent.width
        y: -60
        z: 100
        Row {
            Button {
                text: "Books"
                width: 80
                height: 60
                z: 101
                onClicked: { main.state="Books"; actions.state="Hidden"}
            }
            Button {
                text: "Bookstores"
                width: 80
                height: 60
                z: 101
                onClicked: { main.state="Bookstores"; actions.state="Hidden"}
            }
            Button {
                text: "Bookstore2"
                width: 80
                height: 60
                z: 101
                onClicked: { main.state="Bookstore2"; actions.state="Hidden"}
            }
            Button {
                text: "Contents"
                width: 80
                height: 60
                z: 101
                onClicked: { main.state="Contents"; actions.state="Hidden"}
            }
            Button {
                text: "Read"
                width: 80
                height: 60
                z: 101
                onClicked: { main.state="Text"; actions.state="Hidden"}
            }
        }
        states: [
            State {
                name: "Shown"
                PropertyChanges {
                    target: actions
                    y: 0
                }
            },
            State {
                name: "Hidden"
                PropertyChanges {
                    target: actions
                    y: -60
                }
            }
        ]
        transitions: [
            Transition {
                PropertyAnimation {
                    properties: "y,opacity"
                    duration: 300
                }
            }
        ]
        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            onEntered: { parent.state="Shown" }
            onExited: { parent.state="Hidden" }
            acceptedButtons: Qt.NoButton
        }
    }

    BookList {
        id: booklist
        model: bookList
        contr: controller
        x: 0
        height: parent.height-5
        width: parent.width
        y:5
    }

    BookStoreView {
        id: bookstores
        width: parent.width
        height: parent.height
        anchors.top: booklist.bottom
        anchors.left: booklist.left
        model: bookStoreList
        contr: controller
    }

    BookStoreContents {
        id: bookstorecontents
        anchors.left: bookstores.right
        anchors.top: contents.bottom
        height: parent.height-5
        width: parent.width
        contr: controller
    }


    FlickableWebView {
        id: storewebpage
        anchors.left: bookstorecontents.right
        anchors.top: webview.bottom
        height: parent.height-5
        y:5
    }
    

    FlickableWebView {
        id: webview
        anchors.left: contents.right
        height: parent.height-5
        y:5
    }

    BookContents {
        id: contents
        width: parent.width
        contr: controller
        anchors.left: booklist.right
        anchors.top: booklist.top
        height: parent.height-5
        y:5
    }
   
    states: [
    State {
        name: "Books"
        PropertyChanges {
            target: booklist
            x: 0
            y: 0
        }
    },
    State {
        name: "Bookstores"
        PropertyChanges {
            target: booklist
            x: 0
            y: -parent.height
        }
    },
    State {
        name: "Bookstore2"
        PropertyChanges {
            target: booklist
            x: -1 * parent.width
            y: -parent.height
        }
    },
    State {
        name: "Bookstore3"
        PropertyChanges {
            target: booklist
            x: -2 * parent.width
            y: -parent.height
        }
    },
    State {
        name: "Contents"
        PropertyChanges {
            target: booklist
            x: -1 * parent.width
            y: 0
        }
    },
    State {
        name: "Text"
        PropertyChanges {
            target: booklist
            x: -2 * parent.width
            y: 0
        }
    }
    ]
    transitions: [
        Transition {
            PropertyAnimation {
                properties: "x,y,opacity"
                duration: 500
            }
        }
    ]
}

