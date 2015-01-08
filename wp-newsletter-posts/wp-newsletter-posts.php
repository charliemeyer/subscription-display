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

//------------------------------------------------------------//
//--------------------- TOWN NAME ----------------------------//
//---- Enter the town name here, with it exactly matching ----//
//---- the string before the '@' in the biw-school-news   ----//
//---- email. ex. pembroke@biw-school-news.appspotmail.com ---//
//---- the $town_name variable should be "pembroke". case ----//
//---- counts. If it all breaks, shoot me an email @      ----//
//---- charles.meyer@tufts.edu                            ----// 
//------------------------------------------------------------//

$town_name = "pembroke";

// On activation, set up wordpress to run the add_posts_hourly function hourly
// starting at time of activiation. You can toggle activation/deactivation for testing
// the 'add_posts_hourly' function
register_activation_hook(__FILE__, 'register_on_activation');

function register_on_activation() {
	wp_schedule_event(time(), 'hourly', 'add_posts_hook');
}

add_action('add_posts_hook', 'add_posts_hourly');

// Get the new posts from the server and add them to the blog
// Reference for the parameters in the array @ "http://codex.wordpress.org/Function_Reference/wp_insert_post"
function add_posts_hourly() {
	$slug = 'school-update';
	$response = wp_remote_retrieve_body(wp_remote_get('http://biw-school-news.appspot.com/api?town_name=' + $town_name));
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
				'post_name'		    =>	$slug,
				'post_title'		=>	$title,
				'post_status'		=>	'publish',
				'post_type'		    =>	'post'
			)
		);		
	} 
}	

// On deactivation, stop wordpress from adding posts hourly
register_deactivation_hook(__FILE__, 'remove_on_deactivation');

function remove_on_deactivation() {
	wp_clear_scheduled_hook('add_posts_hook');
}
