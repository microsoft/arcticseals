'use strict';

var app = angular.module('myApp.view2', ['ngRoute'])

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
			var artic = data.Artic;
			var len = artic.length / 2;
			for(var i = 0; i < len; i++) {
				var articI = artic[i];
				$scope.items.push({"idx": i, "file": "thumb-thermal//" + articI.filt_thermal8});
			}
			$scope.$apply();
		}
	});	
});