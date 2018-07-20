'use strict';

var app = angular.module('myApp.view3', ['ngRoute'])

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
			var artic = data.Artic;
			var len = artic.length / 2;
			for(var i = 0; i < len; i++) {
				var articI = artic[i];
				$scope.items.push({"idx": i, "file": "crop-img//" + articI.filt_color});
			}
			$scope.$apply();
		}
	});	
});