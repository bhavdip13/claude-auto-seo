<?php
/**
 * Plugin Name: Claude Auto SEO — Yoast REST API
 * Plugin URI: https://github.com/YOUR_USERNAME/claude-auto-seo
 * Description: Exposes Yoast SEO fields via WordPress REST API for Claude Auto SEO auto-publishing.
 * Version: 1.0.0
 * Author: Claude Auto SEO
 *
 * INSTALLATION:
 * Copy this file to: wp-content/mu-plugins/claude-auto-seo-yoast-rest.php
 * MU-plugins load automatically — no activation needed.
 */

if (!defined('ABSPATH')) exit;

/**
 * Register Yoast SEO meta fields on the REST API for posts and pages.
 */
add_action('rest_api_init', function () {
    $yoast_fields = [
        'yoast_wpseo_title'           => 'SEO Title',
        'yoast_wpseo_metadesc'        => 'SEO Meta Description',
        'yoast_wpseo_focuskw'         => 'Focus Keyword',
        'yoast_wpseo_canonical'       => 'Canonical URL',
        'yoast_wpseo_schema_article_type' => 'Schema Article Type',
        'yoast_wpseo_is_cornerstone'  => 'Is Cornerstone Content',
        'yoast_wpseo_meta-robots-noindex' => 'Noindex',
    ];

    $post_types = ['post', 'page'];

    foreach ($post_types as $post_type) {
        foreach ($yoast_fields as $field_name => $description) {
            register_rest_field($post_type, $field_name, [
                'get_callback' => function ($post_data) use ($field_name) {
                    return get_post_meta($post_data['id'], '_' . $field_name, true);
                },
                'update_callback' => function ($value, $post) use ($field_name) {
                    if ($value === null) return;
                    update_post_meta($post->ID, '_' . $field_name, sanitize_text_field($value));
                    return true;
                },
                'schema' => [
                    'description' => $description,
                    'type'        => 'string',
                    'context'     => ['view', 'edit'],
                ],
            ]);
        }
    }
});

/**
 * Register custom fields for categories and tags on posts.
 */
add_action('rest_api_init', function () {
    register_rest_field('post', 'category_names', [
        'get_callback' => function ($post_data) {
            $cats = get_the_category($post_data['id']);
            return array_map(function ($c) { return $c->name; }, $cats);
        },
        'schema' => ['type' => 'array', 'items' => ['type' => 'string']],
    ]);
});

/**
 * Allow Claude Auto SEO to set featured image by URL.
 */
add_action('rest_api_init', function () {
    register_rest_field('post', 'featured_image_url', [
        'get_callback' => function ($post_data) {
            $thumb_id = get_post_thumbnail_id($post_data['id']);
            return $thumb_id ? wp_get_attachment_url($thumb_id) : null;
        },
        'update_callback' => function ($image_url, $post) {
            if (!$image_url || !filter_var($image_url, FILTER_VALIDATE_URL)) return;

            // Sideload image
            require_once(ABSPATH . 'wp-admin/includes/media.php');
            require_once(ABSPATH . 'wp-admin/includes/file.php');
            require_once(ABSPATH . 'wp-admin/includes/image.php');

            $image_id = media_sideload_image($image_url, $post->ID, null, 'id');
            if (!is_wp_error($image_id)) {
                set_post_thumbnail($post->ID, $image_id);
            }
        },
        'schema' => ['type' => 'string', 'format' => 'uri'],
    ]);
});
