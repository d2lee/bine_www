bineApp.controller('UserControl', ['$scope', '$routeParams', '$upload', 'login_user', 'Users', 'Schools', 'navbar',
    function ($scope, $routeParams, $upload, login_user, Users, Schools, navbar) {
        $scope.init = function () {
            navbar.set_menu('user');

            var user = login_user.get_user();

            $scope.init_birthday();
            $scope.show_account();

            // initialize the date
            var today = new Date()
            $scope.target_from = today;
            $scope.target_to = today;

            var user_id = user.id;
            $scope.user = Users.get({id: user_id}, function () {
                // read data
                $scope.username = $scope.user.username;
                $scope.birth_year = $scope.user.birthday.substr(0, 4);
                $scope.birth_month = $scope.user.birthday.substr(5, 2);
                $scope.birth_day = $scope.user.birthday.substr(8, 2);
                $scope.school = $scope.user.school;
                $scope.fullname = $scope.user.fullname;
                $scope.email = $scope.user.email;
                $scope.sex = $scope.user.sex;
                $scope.photo = $scope.user.photo;
                $scope.tagline = $scope.user.tagline;
                $scope.company = $scope.user.company;
                $scope.target_books = $scope.user.target_books;

                if ($scope.user.target_from)
                    $scope.target_from = new Date($scope.user.target_from);

                if ($scope.user.target_to)
                    $scope.target_to = new Date($scope.user.target_to);
            });

            var action = $routeParams.action;
            if (action == 'm1') {
                $scope.show_account();
            }
            else if (action == 'm2') {
                $scope.show_profile();
            }
            else if (action == 'm3') {
                $scope.show_read_target();
            }
            else {
                // default
                $scope.show_account();
            }


        };

        $scope.show_account = function () {
            $scope.current_menu = 'm1';
            $scope.page_title = "기본정보";
        }

        $scope.show_profile = function () {
            if ($scope.school)
                $scope.school_name = $scope.school.name;
            $scope.http_status = undefined;

            $scope.current_menu = 'm2';
            $scope.page_title = "추가정보";
        }

        $scope.show_read_target = function () {
            $scope.http_status = undefined;

            $scope.current_menu = 'm3';
            $scope.page_title = "독서목표";
        }

        $scope.date_range = function (min, max, step) {
            // parameters validation for method overloading
            if (max == undefined) {
                max = min;
                min = 0;
            }

            step = Math.abs(step) || 1;
            if (min > max) {
                step = -step;
            }
            // building the array
            var output = [];
            var title;

            for (var value = min; value != max; value += step) {
                // adding '0' if it's single digit
                if (value < 10) {
                    title = "0" + value;
                }
                else {
                    title = value;
                }
                // output.push({'text': title, 'value': title});
                output.push(title);
            }

            // output.push({'text': max, 'value': max});
            output.push(max);

            // returning the generated array
            return output;
        };

        $scope.init_birthday = function () {
            $scope.year_list = $scope.date_range((new Date()).getFullYear(), 1910);
            $scope.month_list = $scope.date_range(1, 12);
            $scope.day_list = $scope.date_range(1, 31);
        };

        $scope.set_sex = function (sex) {
            $scope.user.sex = sex;
        };

        $scope.to_iso_format = function (date) {
            if (date) {
                //return $filter('date')(date, 'yyyy-MM-dd')
                return date.toISOString().substr(0, 10);
            }
            return date;
        }

        $scope.get_field_list_to_update = function () {
            var data = {};

            data['id'] = $scope.user.id;

            var birthday = $scope.birth_year + "-" + $scope.birth_month + "-" + $scope.birth_day;

            var target_from = $scope.to_iso_format($scope.target_from);
            var target_to = $scope.to_iso_format($scope.target_to);

            if ($scope.fullname && $scope.fullname != $scope.user.fullname) {
                data['fullname'] = $scope.fullname;
                $scope.user.fullname = $scope.fullname;
            }

            if ($scope.email && $scope.email != $scope.user.email) {
                data['email'] = $scope.email;
                $scope.user.email = $scope.email;
            }

            if ($scope.sex && $scope.sex != $scope.user.sex) {
                data['sex'] = $scope.sex;
                $scope.user.sex = $scope.sex;
            }

            if (birthday && birthday != $scope.user.birthday) {
                data['birthday'] = birthday;
                $scope.user.birthday = $scope.birthday;
            }

            if ($scope.current_password && $scope.password1 && ($scope.password1 == $scope.password2)) {
                data['cp'] = $scope.current_password;
                data['np'] = $scope.password1;
            }

            if ($scope.tagline && $scope.tagline != $scope.user.tagline) {
                data['tagline'] = $scope.tagline;
                $scope.user.tagline = $scope.tagline;
            }

            if (target_from && target_from != $scope.user.target_from) {
                data['target_from'] = target_from;
                $scope.user.target_from = $scope.target_from;
            }

            if (target_to && target_to != $scope.user.target_to) {
                data['target_to'] = target_to;
                $scope.user.target_to = $scope.target_to;
            }

            if ($scope.target_books && $scope.target_books != $scope.user.target_books) {
                data['target_books'] = $scope.target_books;
                $scope.user.target_books = $scope.target_books;
            }

            if ($scope.school) {
                if ($scope.user.school) {
                    if ($scope.school.id != $scope.user.school.id) {
                        data['school'] = $scope.school.id;
                        $scope.user.school = $scope.school;
                    }
                }
                else {
                    data['school'] = $scope.school.id;
                    $scope.user.school = $scope.school;
                }
            }

            return data;
        }

        // 사용자 정보를 업데이트합니다.
        $scope.update_user = function () {
            if (!$scope.user_form.$valid)
                return;

            var data = $scope.get_field_list_to_update();

            if (Object.keys(data).length <= 1)
                return;

            $scope.http_status = undefined;

            Users.update(data, function () {
                $scope.http_status = 200;
                // 변경된 내용을 user 정보에 저장한다.
                new_user_data = {
                    id: $scope.user.id,
                    username: $scope.user.username,
                    fullname: $scope.user.fullname,
                    sex: $scope.user.sex,
                    photo: $scope.user.photo,
                }
                login_user.set_user(new_user_data);

            }, function (response) {
                if (response.status == 403) {
                    $scope.user_form.current_password.$error.wrong_password = true;
                }
                $scope.http_status = response.status;
            });
        }

        $scope.upload = function (files) {
            var file = files[0];
            var user_id = $scope.user.id;

            var url = '/api/user/' + user_id + '/?action=photo';

            if (file) {
                $scope.loading = true;
                $upload.upload({
                    url: url,
                    file: file
                }).progress(function (evt) {
                    // var percent = parseInt(100.0 * evt.loaded / evt.total);
                    // $scope.photo_upload_progress = "{width:" + percent + "%}";
                }).success(function (data, status, headers, config) {
                    $scope.user.photo = data.photo;
                    $scope.loading = false;
                });
            }
        }

        $scope.search_schools = function () {
            var school_name = $scope.school_name;
            $scope.schools = Schools.get_schools({'q': school_name});
        }

        $scope.show_school_search_dlg = function () {
            if ($scope.school_name) {
                $scope.search_schools();
            }
            $('#school_search_modal').modal('show');
        }

        $scope.select_school = function (school) {
            $scope.school = school;
            $scope.school_name = school.name;
            $('#school_search_modal').modal('hide');
        }

        $scope.init();

    }
])
;