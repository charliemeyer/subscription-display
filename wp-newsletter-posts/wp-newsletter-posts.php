<?php
/**
 * Plugin Name: wp-newsletter-posts
 * Plugin URI: https://github.com/charles-meyer/subscription-display
 * Description: Turn newsletter emails into WP posts.
 * Version: 1.0.0
 * Author: Charlie Meyer
 * Author URI: https://github.com/charles-meyer
 * License: GPL2
 */

register_activation_hook( __FILE__, 'prefix_activation');
/**
 * On activation, set a time, frequency and name of an action hook to be scheduled.
 */
function prefix_activation() {
	wp_schedule_event(time(), 'hourly', 'prefix_hourly_event_hook');
}

add_action( 'prefix_hourly_event_hook', 'prefix_do_this_hourly' );
/**
 * On the scheduled action hook, run the function.
 */
function prefix_do_this_hourly() {
	$slug = 'example-post';
	$title = 'Auto-Generated Post' . strval(time());
	$response = wp_remote_retrieve_body(wp_remote_get('http://prefab-kit-801.appspot.com/api?num=20'));
	$data = json_decode($response, true);
	$num_new = intval($data["num_new"]);
	for($i = 0; $i < $num_new; $i++){
		$body = $data["messages"][$i]["body"];
		$title = $data["messages"][$i]["subject"];
		$post_id = wp_insert_post(
			array(
				'post_content'      =>  $body,
				'comment_status'	=>	'closed',
				'ping_status'		=>	'closed',
				'post_author'		=>	'Charlie',
				'post_name'		    =>	$slug,
				'post_title'		=>	$title,
				'post_status'		=>	'publish',
				'post_type'		    =>	'post'
			)
		);		
	} 
}	

register_deactivation_hook( __FILE__, 'prefix_deactivation' );
/**
 * On deactivation, remove all functions from the scheduled action hook.
 */
function prefix_deactivation() {
	wp_clear_scheduled_hook( 'prefix_hourly_event_hook' );
}
