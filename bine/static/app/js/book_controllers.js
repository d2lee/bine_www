bineApp.controller('bookListControl', ['$scope', 'login_user', 'navbar', 'Book',
    function ($scope, login_user, navbar, Book) {
        var init = function () {
            navbar.set_menu('book');
            fetch_book_list();
        }


        // check the authentication
        // $scope.user = login_user.get_user();

        var fetch_book_list = function () {
            Book.query(function(data) {
                $scope.books = data;
                //$scope.noData = !$scope.books.length;
            })
        };

        init();


    }]);