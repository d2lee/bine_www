bineApp.controller('UserControl', ['$scope', '$http', '$upload', 'authService', 'Users', 'Schools',
    function ($scope, $http, $upload, authService, Users, Schools) {
        $scope.init = function () {
            var user = authService.get_user();

            $scope.init_birthday();
            $scope.show_account();

            // initialize the date
            var today = new Date()
            $scope.target_from = today;
            $scope.target_to = today;

            var user_id = user.id;
            $scope.user = Users.get({id: user_id}, function () {
                // initialize the birthday
                $scope.birth_year = $scope.user.birthday.substr(0, 4);
                $scope.birth_month = $scope.user.birthday.substr(5, 2);
                $scope.birth_day = $scope.user.birthday.substr(8, 2);

                if ($scope.user.target_from)
                    $scope.target_from = $scope.user.target_from;

                if ($scope.user.target_to)
                    $scope.target_to = $scope.user.target_to;
            });
        };

        $scope.show_account = function () {
            $scope.current_menu = 'account';
            $scope.page_title = "기본정보";
        }

        $scope.show_profile = function () {
            if ($scope.user.school)
                $scope.school_name = $scope.user.school.name;
            $scope.http_status = undefined;

            $scope.current_menu = 'profile';
            $scope.page_title = "추가정보";
        }

        $scope.show_read_target = function () {
            $scope.http_status = undefined;

            $scope.current_menu = 'read_target';
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

        // 사용자 정보를 업데이트합니다.
        $scope.update_user = function () {
            if (!$scope.user_form.$valid)
                return;

            $scope.user.birthday = $scope.birth_year + "-" + $scope.birth_month + "-" + $scope.birth_day;

            $scope.user.current_password = $scope.current_password;
            $scope.user.password = $scope.password1;
            $scope.http_status = undefined;
            $scope.user.target_from = $scope.toISOformat($scope.target_from);
            $scope.user.target_to = $scope.toISOformat($scope.target_to);

            $scope.user.$update(null, function () {
                $scope.http_status = 200;
            }, function (response) {
                if (response.status == 403) {
                    $scope.user_form.current_password.$error.wrong_password = true;
                }
                $scope.http_status = response.status;
            });
        }

        $scope.toISOformat = function(date) {
            if (date) {
                return date.toISOString().substr(0, 10);
            }
            return date;
        }

        $scope.upload = function (files) {
            var file = files[0];
            var user_id = $scope.user.id;

            var url = '/api/user/' + user_id + '/?action=photo';

            if (file) {
                $upload.upload({
                    url: url,
                    file: file
                }).progress(function (evt) {
                    var progressPercentage = parseInt(100.0 * evt.loaded / evt.total);

                }).success(function (data, status, headers, config) {
                    $scope.user.photo = data.photo;
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
            $scope.user.school = school;
            $scope.school_name = school.name;
            $('#school_search_modal').modal('hide');
        }

        $scope.init();

    }
])
;