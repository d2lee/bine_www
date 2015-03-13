bineApp.controller('NoteListControl', ["$rootScope", "$scope", "$sce",
    "$http", "login_user", "navbar", "BookNotes",
    function ($rootScope, $scope, $sce, $http, login_user, navbar, BookNotes) {
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
            $scope.notes = BookNotes.get_notes_by_all();
        };

        $scope.show_notes_by_me = function () {
            $scope.current_menu = "menu2";
            $scope.notes = BookNotes.get_notes_by_me();
        };


        $scope.make_html_preference = function (preference) {
            var spanHtml = "";

            for (i = 0; i < preference; i++) {
                spanHtml = spanHtml + "<span class='glyphicon glyphicon-star'></span>";
            }

            return $sce.trustAsHtml(spanHtml);
        };

        $scope.edit_note = function (note) {
            $rootScope.note = note;
            location.href = "#/note/new/"
        };

        // 노트를 삭제한다.
        $scope.delete_note = function (note, index) {
            var ret = confirm("노트를 삭제하시겠습니까? 한번 삭제되면 복구할 수 없습니다.");
            if (!ret)
                return;

            var url = "/api/note/" + note.id + "/";
            $http.delete(url).success(function (data) {
                alert('노트가 정상적으로 삭제되었습니다.');
                $scope.notes.splice(index, 1);
            });
        };

        $scope.update_likeit = function (note) {
            var url = "/api/note/" + note.id + "/likeit/";
            $http.post(url).success(function (data) {
                note.likeit = data.likeit;
            });
        };

        $scope.make_html_share = function (share_to) {
            var text = "";
            switch (share_to) {
                case 'P':
                    text = "개인";
                    break;
                case 'F':
                    text = "친구";
                    break;
                case 'A':
                    text = "모두";
                    break;
            }
            return text;
        };

        $scope.make_html_attach = function (attach_url) {
            var html = "";
            if (attach_url) {
                html = "| <a href='/media/" + attach_url + "'>첨부파일(1)</a>";
            }
            return $sce.trustAsHtml(html);
        };

        $scope.init();
    }]);

/*
 자세히 보기 컨트롤러
 */
bineApp.controller('NoteDetailControl', ["$rootScope", "$scope", "$sce", "$routeParams",
    "$http", "login_user", "navbar",
    function ($rootScope, $scope, $sce, $routeParams, $http, login_user, navbar) {
        $scope.init = function () {
            navbar.set_menu('note');
            $scope.user = login_user.get_user();

            // 노트 ID 읽기
            var note_id = $routeParams.note_id;
            if (!note_id) {
                alert('자세히 볼 노트에 대한 정보를 읽을 수 없습니다. 초기화면으로 이동합니다.');
                location.href = "#/note/";
                return;
            }

            $scope.note_id = note_id;
            $scope.new_reply_content = "";
            $scope.current_reply = "";

            $scope.fetch_note_detail(note_id);
            // $scope.fetch_note_reply(note_id);
        };

        $scope.fetch_note_detail = function (note_id) {
            // fetch the details about current booknote.
            var url = '/api/note/' + note_id + "/";
            $http.get(url).success(function (data) {
                $scope.note = data;
            });
        };

        $scope.fetch_note_reply = function (note_id) {
            // fetch the reply information from server.
            var note_reply_url = '/api/note/' + note_id + "/reply/";
            $http.get(note_reply_url).success(function (data) {
                $scope.replies = data;
            });
        };

        // 노트를 삭제한다.
        $scope.delete_note = function () {
            var ret = confirm("노트를 삭제하시겠습니까? 한번 삭제되면 복구할 수 없습니다.");
            if (!ret)
                return;

            var url = "/api/note/" + $scope.note.id + "/";
            $http.delete(url).success(function (data) {
                alert('노트가 정상적으로 삭제되었습니다. 이전 화면으로 이동합니다.');
                window.history.back();
            });
        };

        $scope.edit_note = function (note) {
            if (!note)
                note = $scope.note;

            $rootScope.note = note;
            location.href = "#/note/new/"
        };

        $scope.delete_reply = function (reply, index) {
            var url = url = '/api/note/' + $scope.note_id + '/reply/' + reply.id + "/";

            $http.delete(url).
                success(function (data, status, headers, config) {
                    $scope.replies.splice(index, 1)
                }).
                error(function (data, status, headers, config) {
                    alert("error");
                });
        };

        $scope.update_reply = function (reply) {
            $scope.current_reply = reply;
            $scope.new_reply_content = reply.content;
            $('#reply_modal').modal('show');
        };

        $scope.save_reply = function () {
            if ($scope.new_reply_content != $scope.current_reply.content) {
                $scope.current_reply.content = $scope.new_reply_content;
            }

            var data = {};
            var url = "";

            if ($scope.current_reply == '') { // create
                data = {
                    'user': 2,
                    'content': $scope.new_reply_content
                };
                url = '/api/note/' + $scope.note_id + '/reply/';
            }
            else { // update
                data = {
                    'content': $scope.new_reply_content
                };
                url = '/api/note/' + $scope.note_id + '/reply/' + $scope.current_reply.id + "/";
            }


            $http.post(url, data).
                success(function (data, status, headers, config) {
                    if ($scope.current_reply == '') {
                        $scope.replies.push(data);
                    }

                    $('#reply_modal').modal('hide');
                }).
                error(function (data, status, headers, config) {
                    alert("error");
                });
        };

        $scope.create_reply = function (reply) {
            $scope.new_reply_content = '';
            $scope.current_reply = '';
            $('#reply_modal').modal('show');
        };

        $scope.make_html_preference = function (preference) {
            var spanHtml = "";

            for (i = 0; i < preference; i++) {
                spanHtml = spanHtml + "<span class='glyphicon glyphicon-star'></span>";
            }

            return $sce.trustAsHtml(spanHtml);
        };

        $scope.make_html_share = function (share_to) {
            var text = "";
            switch (share_to) {
                case 'P':
                    text = "개인";
                    break;
                case 'F':
                    text = "친구";
                    break;
                case 'A':
                    text = "모두";
                    break;
            }
            return text;
        };

        $scope.make_html_attach = function (attach_url) {
            var html = "";
            if (attach_url) {
                html = "| <a href='/media/" + attach_url + "'>첨부파일(1)</a>";
            }
            return $sce.trustAsHtml(html);
        };

        $scope.init();
    }]);

/*
 NoteNewControl: 새로운 노트를 생성하거나 기존 노트 수정을 처리하기 위한 컨트롤러
 */
bineApp.controller('NoteNewControl', ["$rootScope", "$scope", "$upload",
    "$http", "login_user", "navbar", "escapeFilter",
    function ($rootScope, $scope, $upload, $http, login_user, navbar, escapeFilter) {

        $scope.init = function () {
            navbar.set_menu('note');
            $scope.user = login_user.get_user();
            $scope.http_status = -1;
            $scope.book_http_status = -1;

            if (!$rootScope.note) { // 새 노트를 생성하려면 기본 값을 채운 노트를 하나 만든다.
                var today = new Date();

                $scope.note = {
                    'user': {'id': $scope.user.id},
                    'preference': 3,
                    'share_to': 'F',
                    'read_date_from': today,
                    'read_date_to': today,
                };
                $scope.book_title = "";
            }
            else {
                $scope.note = $rootScope.note;
                $scope.book_title = $scope.note.book.title;

                // convert string date to date object to initialize input date
                // object.
                $scope.note.read_date_from = new Date($scope.note.read_date_from);
                $scope.note.read_date_to = new Date($scope.note.read_date_to);
            }
        };
        /*
         $scope.stripEscape = function (content) {
         if (content) {
         content = content.replace(/[(&lt;b&gt;)(&lt;/b&gt)]/g, '');
         content = content.replace(/[(&quote;b&quote;)(&quote;/b&quote)]/g, '');
         }
         return content;
         };
         */
        $scope.upload = function (url, data, file) {
            $scope.http_status = -1;

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
                'preference': note.preference,
                'share_to': note.share_to
            };

            var url = '/api/note/';

            if ($scope.note.id != null) { // update
                url = url + $scope.note.id + "/";
            }

            $scope.upload(url, data, $scope.note.attach)
        };

        $scope.set_preference = function (pref) {
            for (var i = 1; i <= 5; i++) {
                if (i <= pref)
                    $('#pref-' + i).css('color', '#337ab7');
                else
                    $('#pref-' + i).css('color', '#333');
            }

            $scope.note.preference = pref;
        };


        $scope.search_book = function () {
            var title = $scope.book_title;

            if (title == '') {
                $('#book_search_modal').modal('show');

            }
            else {
                var url = "https://apis.daum.net/search/book";
                //var api_key = "3cf83b5f4a7062c5e99173f7759b6a2e"; // production
                var api_key = "8f9f9bc97bfa50b4fd80e589f0384f56"; // test

                url += "?output=json&result=10&sort=popular";
                url += "&apikey=" + api_key;
                url += "&q=" + title;
                url += "&callback=JSON_CALLBACK";
                $scope.book_http_status = -1;
                $http.jsonp(url).
                    success(function (data, status, headers, config) {
                        $scope.books = $scope.strip_escaped_characters(data.channel.item);
                        $('#book_search_modal').modal('show');
                        $scope.book_http_status = 200;
                    }).
                    error(function (data, status, headers, config) {
                        $scope.book_http_status = status;
                    });
            }
        };

        $scope.strip_escaped_characters = function (books) {
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
                'author': escapeFilter(book.author),
                'title': escapeFilter(book.title),
                'isbn': book.isbn,
                'isbn13': book.isbn13,
                'barcode': book.barcode,
                'author_etc': escapeFilter(book.etc_author),
                'translator': escapeFilter(book.translator),
                'photo': book.cover_s_url,
                'description': escapeFilter(book.description),
                'category': escapeFilter(book.category),
                'publisher': escapeFilter(book.pub_nm),
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