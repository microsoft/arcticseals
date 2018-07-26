'use strict';

var app = angular.module('myApp.view4', ['ngRoute'])
var artic, items;
var getName = function(articI) {
	var names = articI.filt_color.split(".");
	var name = names[0] + "." + names[1] + "_HOTSPOT_" + articI.hotspot_id + ".JPG";
	return name;
};

app.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/view4', {
    templateUrl: 'view4/view4.html',
    controller: 'View4Ctrl'
  });
}])

app.controller('View4Ctrl', function($scope) {
	$scope.items = [];

	var json = null;

	$.getJSON( "/data/training.json", function( data ) {
		if (data.Artic !== 'undefined') {
			var artic = data.Artic;
			var len = artic.length / 2;
			for(var i = 0; i < len; i++) {
				var articI = artic[i];
				$scope.items.push({"idx": i, "color": "thumb-img//" + articI.filt_color, "thermal" : "thumb-thermal//" + articI.filt_thermal8});
			}
			$scope.$apply();
		}
	});

	$scope.filterMe = function( hotspot_type ) {
		if (artic !== 'undefined') {
			$scope.items = [];
			var len = artic.length / 3;
			for(var i = 0; i < len; i++) {
				var name = getName(artic[i]);
				if (artic[i].hotspot_type === hotspot_type) {
					$scope.items.push({"idx": i, "file": "crop-img//" + name});				
				}
			}
			items = $scope.items;
			$scope.$apply();
		}
	};

});