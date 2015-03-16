bineApp.controller('NoteListControl', ["$rootScope", "$scope", "$location",
    "login_user", "navbar", "BookNotes",
    function ($rootScope, $scope, $location, login_user, navbar, BookNotes) {
        $scope.init = function () {
            navbar.set_menu('note');

            $scope.http_status = -1;
            $rootScope.note = null;
            $scope.user = login_user.get_user();
            $scope.note_state = BookNotes.get_notes_count(null, function () {
                if ($scope.note_state.target_max)
                    $scope.note_state.target_percent = $scope.note_state.target_count / $scope.note_state.target_max * 100;
            })

            $scope.show_notes_by_all();
        };

        $scope.show_notes_by_all = function () {
            $scope.current_menu = "menu1";
            BookNotes.get_notes_by_all(function (data) {
                $scope.notes = data;

            });
        };

        $scope.show_notes_by_me = function () {
            $scope.current_menu = "menu2";
            BookNotes.get_notes_by_me(function (data) {
                $scope.notes = data;
            });
        };


        $scope.edit_note = function (note) {
            var note_id = note.id;
            var url = "/note/form/" + note_id + "/";
            $location.url(url);
        };

        // 노트를 삭제한다.
        $scope.delete_note = function (note, index) {
            var ret = confirm("노트를 삭제하시겠습니까? 한번 삭제되면 복구할 수 없습니다.");
            if (!ret)
                return;

            note.$delete(function (data) {
                alert('노트가 정상적으로 삭제되었습니다.');
                $scope.notes.splice(index, 1);
            });
        };

        $scope.init();
    }]);

/*
 자세히 보기 컨트롤러
 */
bineApp.controller('NoteDetailControl', ["$scope", "$routeParams", "$location", "login_user",
    "navbar", "BookNotes",
    function ($scope, $routeParams, $location, login_user, navbar, BookNotes) {
        $scope.init = function () {
            navbar.set_menu('note');

            $scope.note_id = note_id;
            $scope.rating = 1;

            // 노트 ID 읽기
            var note_id = $routeParams.note_id;
            if (!note_id)
                go_back_if_invalid_note_id();

            fetch_note_detail(note_id);
        };

        var go_back_if_invalid_note_id = function () {
            alert('노트를 찾을 수 없습니다. 이전 메뉴로 이동합니다.');
            window.history.back();
        }
        var go_back_if_invalid_user_id = function () {
            alert('현재 로그인 사용자 권한으로 볼 수 없습니다.');
            $location.url("/note/");
        }

        var check_valid_user = function (note) {
            var current_user = login_user.get_user();
            var note_user = note.user;

            if (current_user && note_user && current_user.id == note_user.id || note.share_to == 'F' || note.share_to == 'A')
                return true;
            else
                return false;

        }

        var fetch_note_detail = function (note_id) {
            BookNotes.get({noteId: note_id}, function (data) {
                if (!check_valid_user(data)) {
                    go_back_if_invalid_user_id();
                }
                $scope.note = data;
                $scope.rating = $scope.note.rating;
            }, function (data) {
                if (data.status == 404) {
                    go_back_if_invalid_note_id();
                }
                if (data.status == 401) {
                    go_back_if_invalid_user_id();
                }
            });
        };

        // 노트를 삭제한다.
        $scope.delete_note = function () {
            var ret = confirm("노트를 삭제하시겠습니까? 한번 삭제되면 복구할 수 없습니다.");
            if (!ret)
                return;

            $scope.note.$delete(function () {
                alert('노트가 정상적으로 삭제되었습니다. 이전 화면으로 이동합니다.');
                window.history.back();
            });
        };

        // 노트를 수정하기 위해 수정화면으로 이동한다.
        $scope.edit_note = function () {
            var note_id = $scope.note.id;
            var url = "/note/form/" + note_id + "/";
            location.url(url);
        };

        $scope.init();
    }]);

/*
 NoteNewControl: 새로운 노트를 생성하거나 기존 노트 수정을 처리하기 위한 컨트롤러
 */
bineApp.controller('NoteFormControl', ["$routeParams", "$scope", "$upload",
    "$http", "$location", "login_user", "navbar", "BookNotes", "BookSearchAPI",
    function ($routeParams, $scope, $upload, $http, $location, login_user, navbar, BookNotes, BookSearchAPI) {

        $scope.init = function () {
            navbar.set_menu('note');
            $scope.user = login_user.get_user();
            $scope.http_status = -1;
            $scope.book_http_status = -1;
            $scope.rating = 1;

            var note_id = $routeParams.note_id;

            if (note_id) {
                fetch_note_detail(note_id);
            }
            else {
                $scope.note = create_empty_note_with_default();
                $scope.book_title = "";
                $scope.rating = 3;
            }
        };

        var create_empty_note_with_default = function () {
            // Create new note
            var today = new Date();

            var note = {
                'user': {'id': $scope.user.id},
                'rating': 3,
                'share_to': 'F',
                'read_date_from': today,
                'read_date_to': today
            };

            return note;
        }

        var go_back_if_invalid_note_id = function () {
            alert('노트를 찾을 수 없습니다. 이전 메뉴로 이동합니다.');
            window.history.back();
        }

        var go_back_if_invalid_user_id = function () {
            alert('현재 로그인 사용자 권한으로 수정할 수 없습니다.');
            $location.url("/note/");
        }

        var check_valid_user = function (note) {
            var current_user = login_user.get_user();
            var note_user = note.user;

            if (current_user && note_user && current_user.id == note_user.id)
                return true;
            else
                return false;

        }

        var fetch_note_detail = function (note_id) {
            BookNotes.get({noteId: note_id}, function (data) {
                if (!check_valid_user(data)) {
                    go_back_if_invalid_user_id();
                }
                ;

                $scope.note = data;

                $scope.book_title = $scope.note.book.title;
                $scope.rating = data.rating;
                // convert string date to date object to initialize input date
                // object.
                $scope.note.read_date_from = new Date($scope.note.read_date_from);
                $scope.note.read_date_to = new Date($scope.note.read_date_to);

            }, function (data) {
                if (data.status == 404) {
                    go_back_if_invalid_note_id();
                }

                if (data.status == 401) {
                    go_back_if_invalid_user_id();
                }
            });
        };

        $scope.upload = function (url, data, file) {
            $scope.http_status = -1;
            data.rating = $scope.rating;

            $upload.upload({
                url: url,
                method: 'POST',
                fields: data,
                fileFormDataName: 'attach',
                file: file
            }).progress(function (evt) {

            }).success(function (data, status, headers, config) {
                $scope.http_status = status;

            }).error(function (data, status) {
                $scope.http_status = status;
            })
        };

        /*
         기존 BookNote를 수정하거나 새로운 노트를 저장한다.
         */
        $scope.save = function () {
            var note = $scope.note;
            var id = "";

            if (!$scope.note_form.$valid)
                return;

            if (note.id)
                id = note.id;

            var data = {
                'id': id,
                'user': note.user.id,
                'book': note.book.id,
                'content': note.content,
                'read_date_from': $scope.format_date(note.read_date_from),
                'read_date_to': $scope.format_date(note.read_date_to),
                'rating': note.rating,
                'share_to': note.share_to
            };

            var url = '/api/note/';

            if ($scope.note.id != null) { // update
                url = url + $scope.note.id + "/";
            }

            $scope.upload(url, data, $scope.note.attach)
        };

        $scope.search_book = function () {
            var title = $scope.book_title;

            if (title == '') {
                $('#book_search_modal').modal('show');
            }
            else {
                // key
                BookSearchAPI.get(function (data) {
                    var api_key = data.key;
                    if (api_key) {
                        var url = "https://apis.daum.net/search/book";
                        url += "?output=json&result=10&sort=popular";
                        url += "&apikey=" + api_key;
                        url += "&q=" + title;
                        url += "&callback=JSON_CALLBACK";
                        $scope.book_http_status = -1;
                        $http.jsonp(url).
                            success(function (data, status, headers, config) {
                                $scope.books = $scope.strip_escaped_text(data.channel.item);
                                $('#book_search_modal').modal('show');
                                $scope.book_http_status = 200;
                            }).
                            error(function (data, status, headers, config) {
                                $scope.book_http_status = status;
                            });
                    }
                    else {
                        alert('서버나 네트워크 이상으로 지금 책 검색을 할 수 없습니다. 잠시 후에 시도해 주십시오. ')
                    }
                })


            }
        };

        $scope.strip_escaped_text = function (books) {
            var jsonText = angular.toJson(books);

            // remove double quote for json
            jsonText = jsonText.replace(/&quot;/g, '\\"');

            jsonText = $('<div/>').html(jsonText).text();
            jsonText = $('<div/>').html(jsonText).text();

            return angular.fromJson(jsonText);
        }

        $scope.add_dash_to_date = function (d) {
            return d.substr(0, 4) + "-" + d.substr(4, 2) + "-" + d.substr(6, 2)
        };

        $scope.save_book = function (book) {
            // 새로운 책이기 때문에 데이터베이스에 저장.
            var book_data = {
                'author': book.author,
                'title': book.title,
                'isbn': book.isbn,
                'isbn13': book.isbn13,
                'barcode': book.barcode,
                'author_etc': book.etc_author,
                'translator': book.translator,
                'photo': book.cover_s_url,
                'description': book.description,
                'category': book.category,
                'publisher': book.pub_nm,
                'pub_date': $scope.add_dash_to_date(book.pub_date),
                'link': book.link
            };

            url = '/api/book/';
            $http.post(url, book_data).success(function (data, status, headers, config) {
                $scope.note.book = data;
                $scope.book_title = book.title;
                $('#book_search_modal').modal('hide');
            }).error(function (data, status, headers, config) {
                alert("서버에 이상이 있습니다. 잠시후에 다시 시도해 주십시오.");

            });
        };

        // 사용자가 책을 선택했을 때 실행되는 함수
        $scope.select_book = function (book) {

            // 이미 데이터베이스에 존재하는지 유무 확인
            var url = "/api/book/isbn13/" + book.isbn13 + "/";
            $http.get(url).success(function (data, status, headers, config) {
                $scope.note.book = data;
                $scope.book_title = book.title;
                $('#book_search_modal').modal('hide');
            }).error(function (data, status, headers, config) {
                if (status == 404) {
                    // 새로운 책이기 때문에 데이터베이스에 저장.
                    $scope.save_book(book);
                }
                else {
                    alert('서버에 이상이 있습니다. 잠시후에 다시 시도해 주십시오.');
                }
            });
        };

        $scope.format_date = function (date) {
            var year = date.getFullYear();
            var month = (1 + date.getMonth()).toString();
            month = month.length > 1 ? month : '0' + month;
            var day = date.getDate().toString();
            day = day.length > 1 ? day : '0' + day;
            return year + '-' + month + '-' + day;
        };

        $scope.go_back = function () {
            window.history.back();
        };

        $scope.reset = function (clear) {
            if (clear) {
                $scope.init();
            }
            else {
                $scope.http_status = -1;
            }
        };

        // init 함수 호출
        $scope.init();
    }
]);