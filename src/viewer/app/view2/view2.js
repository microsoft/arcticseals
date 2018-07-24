'use strict';

var app = angular.module('myApp.view2', ['ngRoute'])
var artic;
var getName = function(articI) {
	var names = articI.filt_color.split(".");
	var name = names[0] + "." + names[1] + "_HOTSPOT_" + articI.hotspot_id + ".JPG";
	return name;
};

app.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/view2', {
    templateUrl: 'view2/view2.html',
    controller: 'View2Ctrl'
  });
}])

app.controller('View2Ctrl', function($scope) {
	$scope.items = [];

	var json = null;
	$.getJSON( "/data/training.json", function( data ) {
		if (data.Artic !== 'undefined') {
			artic = data.Artic;
			var len = artic.length;
			for(var i = 0; i < len; i++) {
				var articI = artic[i];
				$scope.items.push({"idx": i, "file": "thumb-thermal//" + articI.filt_thermal8});
			}
			$scope.$apply();
		}
	});

	$scope.filterMe = function( hotspot_type ) {
		if (artic !== 'undefined') {
			$scope.items = [];
			var len = artic.length;
			for(var i = 0; i < len; i++) {
				if (artic[i].hotspot_type === hotspot_type) {
					$scope.items.push({"idx": i, "file": "thumb-thermal//" + artic[i].filt_thermal8});				
				}
			}
			$scope.$apply();
		}
	};

});