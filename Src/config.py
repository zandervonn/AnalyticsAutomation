#todo split into different config text files
shopify_defined_subheaders_orders = [
	'order_number',
	'updated_at',
	'contact_email',
	'total_line_items_price',
	'discount_codes.code',
	'discount_codes.amount',
	'current_subtotal_price',
	'total_shipping_price_set.shop_money.amount',
	'total_tip_received',
	'current_total_price',
	'current_total_tax',
	'landing_site',
	'name',
	'note',
	'payment_gateway_names',
	'tags'
	# 'confirmation_number',
	# 'total_weight',
	# 'customer.id',
	# 'customer.email',
	# 'customer.first_name',
	# 'customer.last_name',
	# 'line_items.id',
	# 'line_items.name',
	# 'line_items.price',
	# 'fulfillments.id',
	# 'fulfillments.created_at',
]

shopify_defined_subheaders_customers = [
	'id',
	'email',
	'created_at',
	# 'updated_at',
	'first_name',
	'last_name',
	'orders_count',
	# 'state',
	'total_spent',
	'last_order_id',
	'note',
	# 'verified_email',
	# 'multipass_identifier',
	# 'tax_exempt',
	'tags',
	'last_order_name',
	# 'currency',
	# 'phone',
	# 'addresses.id',
	# 'addresses.customer_id',
	# 'addresses.first_name',
	# 'addresses.last_name',
	# 'addresses.company',
	# 'addresses.address1',
	# 'addresses.address2',
	'addresses.city',
	# 'addresses.province',
	# 'addresses.country',
	# 'addresses.zip',
	# 'addresses.phone',
	# 'addresses.name',
	# 'addresses.province_code',
	# 'addresses.country_code',
	'addresses.country_name',
	# 'addresses.default',
	# 'tax_exemptions',
	'email_marketing_consent.state',
	# 'email_marketing_consent.opt_in_level',
	# 'email_marketing_consent.consent_updated_at',
	# 'sms_marketing_consent.state',
	# 'sms_marketing_consent.opt_in_level',
	# 'sms_marketing_consent.consent_updated_at',
	# 'sms_marketing_consent.consent_collected_from',
	# 'admin_graphql_api_id',
	# 'default_address.id',
	# 'default_address.customer_id',
	# 'default_address.first_name',
	# 'default_address.last_name',
	# 'default_address.company',
	# 'default_address.address1',
	# 'default_address.address2',
	# 'default_address.city',
	# 'default_address.province',
	# 'default_address.country',
	# 'default_address.zip',
	# 'default_address.phone',
	# 'default_address.name',
	# 'default_address.province_code',
	# 'default_address.country_code',
	# 'default_address.country_name',
	# 'default_address.default'
]


starshipit_defined_subheaders = [
	'order_id',
	'order_date',
	'shipped_date',
	'order_number',
	# 'status',
	'order_type',
	'reference',
	'carrier',
	'carrier_name',
	'carrier_service_code',
	'shipping_method',
	# 'signature_required',
	# 'dangerous_goods',
	# 'currency',
	# 'sender_details.name',
	# 'sender_details.email',
	# 'sender_details.phone',
	# 'sender_details.street',
	# 'sender_details.suburb',
	# 'sender_details.city',
	# 'sender_details.state',
	# 'sender_details.post_code',
	# 'sender_details.country',
	# 'destination.name',
	# 'destination.email',
	# 'destination.street',
	# 'destination.suburb',
	# 'destination.city',
	# 'destination.state',
	'destination.post_code',
	'destination.country',
	# 'items.description',
	# 'items.sku',
	# 'items.country_of_origin',
	'items.quantity',
	'items.weight',
	# 'items.value',
	'packages.name',
	'packages.weight',
	# 'packages.height',
	# 'packages.width',
	# 'packages.length',
	'packages.packaging_type',
	# 'metadatas.metafield_key',
	# 'metadatas.value',
	'declared_value',
	# 'archived',
	# 'manifest_number',
	# 'address_validation',
	# 'create_return',
	# 'dtp',
	# 'add_insurance',
	# 'insurance_value',
	# 'plt',
	# 'type',
	# 'platform',
]

# https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema
#limit of 10
google_defined_headers_metrics = [
	# activeUsers
	# addToCarts
	# advertiserAdClicks
	# advertiserAdCost
	# advertiserAdCostPerClick
	# advertiserAdCostPerConversion
	# advertiserAdImpressions
	# averagePurchaseRevenue
	# averagePurchaseRevenuePerPayingUser
	# averagePurchaseRevenuePerUser
	# averageRevenuePerUser
	# averageSessionDuration
	# cartToViewRate
	# checkouts
	# conversions
	# newUsers
	# organicGoogleSearchAveragePosition
	# organicGoogleSearchClickThroughRate
	# organicGoogleSearchClicks
	# organicGoogleSearchImpressions
	# returnOnAdSpend
	# totalRevenue
	# totalUsers
	# transactions
	# userConversionRate
	# userEngagementDuration


	# "sessions",
	# "addToCarts",
	# "checkouts",
	# "transactions",
	# "averagePurchaseRevenue",
	# "bounceRate",
	# "eventsPerSession",
	# "advertiserAdCostPerClick",
	# "advertiserAdCostPerConversion",
	# "engagedSessions",
	# "firstTimePurchasers",
	# "grossPurchaseRevenue",
	# "itemDiscountAmount",
	# "itemsViewed",
	# "itemsPurchased",
	# "organicGoogleSearchAveragePosition",
	# "organicGoogleSearchClicks",
	# "promotionClicks",
	# "transactionsPerPurchaser",
	# "userEngagementDuration"
]

# https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema
# limit of 9
google_defined_headers_dimensions = [
	# "adFormat",
	# "adSourceName",
	# "brandingInterest",
	# "campaignName",
	# "City",
	# "Country",
	# "deviceCategory",
	# "googleAdsAdGroupName",
	# "googleAdsAdNetworkType",
	# "googleAdsCampaignName",
	# "googleAdsKeyword",
	# "pageReferrer",
	# "platform",
	# "Region",
	# "Source",
	# "userAgeBracket",
	# "userGender",

	# "date",
	# "dateHour",
	# "dateHourMinute",
	# "dayOfWeekName",
	# "sessionSource"
]

cin7_defined_subheaders = [
	'id',
	'status',
	'createdDate',
	'modifiedDate',
	# 'styleCode',
	'name',
	# 'tags',
	'brand',
	'category',
	'subCategory',
	# 'channels',
	'weight',
	# 'height',
	# 'width',
	# 'length',
	# 'volume',
	'stockControl',
	'orderType',
	'productType',
	# 'optionLabel1',
	'salesAccount',
	# 'productOptions.id',
	'productOptions.status',
	'productOptions.productId',
	# 'productOptions.code',
	# 'productOptions.barcode',
	# 'productOptions.option1',
	'productOptions.optionWeight',
	'productOptions.retailPrice',
	# 'productOptions.wholesalePrice',
	# 'productOptions.vipPrice',
	# 'productOptions.specialPrice',
	'productOptions.stockAvailable',
	'productOptions.stockOnHand',
	# 'productOptions.priceColumns.retailNZD',
	# 'productOptions.priceColumns.vipnzd',
	# 'productOptions.priceColumns.wholesaleNZD',
	# 'productOptions.priceColumns.priceAUD',
	# 'productOptions.priceColumns.priceUSD',
	'productOptions.priceColumns.costNZD',
	# 'productOptions.priceColumns.costUSD',
	# 'productOptions.priceColumns.costAUD',
	# 'productOptions.priceColumns.specialPrice'
]

#insights?pretty=0&since=1707379200&until=1707897600&metric=post_engaged_users&period=day
facebook_insights_headers = [
	"page_total_actions", # empty
	"page_get_directions_clicks_logged_in_unique", #empty
	"page_engaged_users",
	"page_post_engagements",
	"page_consumptions",
	"page_consumptions_by_consumption_type.link clicks",
	"page_consumptions_by_consumption_type.other clicks",
	"page_consumptions_by_consumption_type.photo view",
	"page_consumptions_by_consumption_type.video play",
	"page_negative_feedback_by_type.hide clicks",
	"page_negative_feedback_by_type.hide all clicks",
	"page_negative_feedback_by_type.report spam clicks",
	"page_negative_feedback_by_type.unlike page clicks",
	"page_positive_feedback_by_type.claim",
	"page_positive_feedback_by_type.comment",
	"page_positive_feedback_by_type.like",
	"page_positive_feedback_by_type.link",
	"page_positive_feedback_by_type.other",
	"page_positive_feedback_by_type.rsvp",
	"page_impressions", # 44k
	"page_impressions_paid",
	"page_impressions_organic_v2", # 1.5k
	"page_impressions_by_story_type.checkin",
	"page_impressions_by_story_type.coupon",
	"page_impressions_by_story_type.event",
	"page_impressions_by_story_type.fan",
	"page_impressions_by_story_type.mention",
	"page_impressions_by_story_type.page post",
	"page_impressions_by_story_type.question",
	"page_impressions_by_story_type.user post",
	"page_impressions_by_story_type.other",
	"page_impressions_by_city_unique",
	"page_impressions_by_country_unique",
	"page_impressions_by_age_gender_unique",
	"page_posts_impressions",
	"page_posts_impressions_paid",
	"page_posts_impressions_organic",
	"post_engaged_users", # empty
	"post_negative_feedback_by_type.hide clicks", # empty
	"post_negative_feedback_by_type.hide all clicks", # empty
	"post_negative_feedback_by_type.report spam clicks", # empty
	"post_negative_feedback_by_type.unlike page clicks",  # empty
	"post_clicks", #empty
	"page_fans",
	"page_fans_city",
	"page_fan_removes", #empty
	"page_fans_by_like_source.News Feed",
	"page_fans_by_like_source.Page Suggestions",
	"page_fans_by_like_source.Restored Likes from Reactivated Accounts",
	"page_fans_by_like_source.Search,Your Page",

	# page_video_views
	# page_video_views_paid
	# page_video_views_organic
	# page_video_complete_views_30s
	# page_video_complete_views_30s_paid
	# page_video_complete_views_30s_organic
	# "page_views_total" # working
	# "page_content_activity_by_action_type_unique" # working, curly list
	# 'page_total_actions',
	# 'page_engaged_users',
	# 'page_impressions_organic_v2',
	# 'page_fan_removes_unique',
	# 'page_fans_by_like_source'
	# 'page_impressions',
	# 'page_views_total',
	# 'page_fan_adds_unique'
]

instagram_insights_headers = [
	"impressions",
	# "reach",
	# "follower_count",
	# "email_contacts",
	# "phone_call_clicks",
	# "text_message_clicks",
	# "get_directions_clicks",
	# "website_clicks",
	# "profile_views",
	# "audience_gender_age",
	# "audience_locale",
	# "audience_country",
	# "audience_city",
	# "online_followers",
	# "accounts_engaged",
	# "total_interactions",
	# "likes",
	# "comments",
	# "shares",
	# "saves",
	# "replies",
	# "engaged_audience_demographics",
	# "reached_audience_demographics",
	# "follower_demographics",
	# "follows_and_unfollows",
	# "profile_links_taps"
]