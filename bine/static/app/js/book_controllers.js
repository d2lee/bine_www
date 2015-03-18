bineApp.controller('bookListControl', ['$scope', 'login_user', 'navbar', 'Book',
    function ($scope, login_user, navbar, Book) {
        var init = function () {
            navbar.set_menu('book');
            fetch_book_list();
        }


        // check the authentication
        // $scope.user = login_user.get_user();

        var fetch_book_list = function () {
            Book.query(function (data) {
                $scope.books = data;
            })
        };

        init();


    }]);

bineApp.controller('bookDetailControl', ['$scope', '$routeParams', 'login_user', 'navbar', 'Book', 'BookNotes',
    function ($scope, $routeParams, login_user, navbar, Book, BookNotes) {
        var init = function () {
            navbar.set_menu('book');

            // 노트 ID 읽기
            var book_id = $routeParams.book_id;
            if (!book_id)
                go_back_if_invalid_id();

            $scope.avg_rating = 1;

            fetch_book_detail(book_id);
            fetch_notes_list(book_id);

        };

        var go_back_if_invalid_id = function () {
            alert('책을 찾을 수 없습니다. 이전 메뉴로 이동합니다.');
            window.history.back();
        }

        var fetch_book_detail = function (book_id) {
            Book.get({bookId: book_id}, function (data) {
                $scope.book = data;
                $scope.avg_rating = data.avg_rating;
            }, function (data) {
                if (data.status == 404) {
                    go_back_if_invalid_id();
                }
            });
        }

        var fetch_notes_list = function (book_id) {
            BookNotes.get_notes_by_book({'book':book_id}, function(data) {
                $scope.notes = data;
            })
        }

        init();
    }]);