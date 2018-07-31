'use strict';

var app = angular.module('myApp.view3', ['ngRoute'])
var artic, items;
var getName = function(articI) {
	var names = articI.filt_color.split(".");
	var name = names[0] + "." + names[1] + "_HOTSPOT_" + articI.hotspot_id + ".JPG";
	return name;
};

app.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/view3', {
    templateUrl: 'view3/view3.html',
    controller: 'View3Ctrl'
  });
}])

app.controller('View3Ctrl', function($scope) {
	$scope.items = [];

	var json = null;
	$.getJSON( "/data/training.json", function( data ) {
		if (data.Artic !== 'undefined') {
			artic = data.Artic;
			var len = artic.length / 3;
			for(var i = 0; i < len; i++) {
				var name = getName(artic[i]);
				$scope.items.push({"idx": i, "file": "crop-img//" + name});
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