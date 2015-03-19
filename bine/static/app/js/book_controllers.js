bineApp.controller('bookListControl', ['$scope', 'login_user', 'navbar', 'Book',
    function ($scope, login_user, navbar, Book) {
        var PAGE_ITEM_COUNT = 10;

        var init = function () {
            navbar.set_menu('book');

            $scope.last_page = false;
        }

        var fetch_book_list = function () {
            if ($scope.last_page) { // if last page, we don't need to fetch new data.
                return;
            }

            $scope.is_busy = true;

            var next_page;
            if ($scope.books) {
                next_page = Math.round($scope.books.length / PAGE_ITEM_COUNT) + 1;
            }
            else {
                next_page = 1;
            }
            var page_data = {'page': next_page}

            Book.query(page_data, function (data) {
                if (data.length > 0) {
                    if ($scope.books) {
                        for (var i = 0; i < data.length; i++) {
                            $scope.books.push(data[i]);
                        }
                    }
                    else {
                        $scope.books = data;
                    }
                }
                else { // no content means last page.
                    console.log('last_page set!');
                    $scope.last_page = true;
                }
                $scope.is_busy = false;
            }, function () {
                $scope.is_busy = false;
            });
        };

        $scope.next_page = function () {
            if (!$scope.is_busy) {
                fetch_book_list();
            }
        }

        $scope.images = [1, 2, 3, 4, 5, 6, 7, 8];

        $scope.loadMore = function () {
            var last = $scope.images[$scope.images.length - 1];
            for (var i = 1; i <= 8; i++) {
                $scope.images.push(last + i);
            }
        };

        init();
    }]);

bineApp.controller('bookDetailControl', ['$scope', '$routeParams', 'login_user', 'navbar', 'Book', 'BookNotes',
    function ($scope, $routeParams, login_user, navbar, Book, BookNotes) {
        var PAGE_ITEM_COUNT = 10;

        var init = function () {
            navbar.set_menu('book');

            // 노트 ID 읽기
            $scope.book_id = $routeParams.book_id;
            if (!$scope.book_id)
                go_back_if_invalid_id();

            $scope.avg_rating = 1;

            fetch_book_detail();


            // fetch_notes_list(book_id);
        };

        var go_back_if_invalid_id = function () {
            alert('책을 찾을 수 없습니다. 이전 메뉴로 이동합니다.');
            window.history.back();
        }

        var fetch_book_detail = function () {
            var book_id = $scope.book_id;

            Book.get({bookId: book_id}, function (data) {
                $scope.book = data;
                $scope.avg_rating = data.avg_rating;
            }, function (data) {
                if (data.status == 404) {
                    go_back_if_invalid_id();
                }
            });
        }

        var fetch_notes_list = function () {
            var book_id = $scope.book_id;

            if ($scope.last_page) { // if last page, we don't need to fetch new data.
                return;
            }

            $scope.is_busy = true;

            var next_page;
            if ($scope.notes) {
                next_page = Math.round($scope.notes.length / PAGE_ITEM_COUNT) + 1;
            }
            else {
                next_page = 1;
            }
            var request_data = {'book': book_id, 'page': next_page}

            BookNotes.get_notes_by_book(request_data, function (data) {
                if (data.length > 0) {
                    if ($scope.notes) {
                        for (var i = 0; i < data.length; i++) {
                            $scope.notes.push(data[i]);
                        }
                    }
                    else {
                        $scope.notes = data;
                    }
                }
                else { // no content means last page.
                    $scope.last_page = true;
                }
                $scope.is_busy = false;
            }, function () {
                $scope.is_busy = false;
            });
        }

        $scope.next_page = function() {
            if (!$scope.is_busy) {
                fetch_notes_list();
            }
        }

        init();
    }]);