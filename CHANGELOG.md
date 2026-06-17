## Unreleased

To `grid` command add `--color` argument.

Add icons:
  - `cable_barrier` ([#57](https://github.com/enzet/Roentgen/issues/57)),
  - `pan_and_spoon`,
  - `planet`,
  - `planet_with_stars`,
  - `rope_barrier`.

Redraw icons:
  - `chain_barrier`.


## 0.16.0

Add new type of SVG sketch files supported by iconscript 0.4.

Add icons:
  - `arrow_backward`,
  - `arrow_forward`,
  - `barrier_jersey` ([#51](https://github.com/enzet/Roentgen/issues/51)),
  - `bee` ([#47](https://github.com/enzet/Roentgen/issues/47)),
  - `bus_over_bus_trap` ([#53](https://github.com/enzet/Roentgen/issues/53)),
  - `compass`,
  - `compass_rose`,
  - `full_height_turnstile`
    ([#52](https://github.com/enzet/Roentgen/issues/52)),
  - `narrow_gauge`,
  - `rails`,
  - `rails_with_derailer` ([#56](https://github.com/enzet/Roentgen/issues/56)),
  - `tactile_map` ([#11](https://github.com/enzet/Roentgen/issues/11)),
  - `tumulus`,
  - `vending_candy` ([#45](https://github.com/enzet/Roentgen/issues/45)),
  - `vending_lollipop` ([#45](https://github.com/enzet/Roentgen/issues/45)),
  - `vending_pack` ([#43](https://github.com/enzet/Roentgen/issues/43)),

Redraw icons:
  - `bus`,
  - `saddle`,
  - `trolleybus`.

To `grid` command add `--width`, `--height` and `--background` arguments.


## 0.15.0

Create `shapes` directory with `icons` command.

Add icons:
  - `advertising_totem` ([#32](https://github.com/enzet/Roentgen/issues/32)),
  - `breakwater` ([#39](https://github.com/enzet/Roentgen/issues/39)),
  - `building_part` ([#48](https://github.com/enzet/Roentgen/issues/48)),
  - `building_with_plant` ([#40](https://github.com/enzet/Roentgen/issues/40)),
  - `circle_with_dot` ([#46](https://github.com/enzet/Roentgen/issues/46)),
  - `dam` ([#39](https://github.com/enzet/Roentgen/issues/39)),
  - `dead_tree` ([#29](https://github.com/enzet/Roentgen/issues/29)),
  - `millstone_with_furrows`
    ([#46](https://github.com/enzet/Roentgen/issues/46)),
  - `person_bungee_jumping`
    ([#38](https://github.com/enzet/Roentgen/issues/38)),
  - `person_throwing_spear`
    ([#35](https://github.com/enzet/Roentgen/issues/35)),
  - `sinking_ship` ([#34](https://github.com/enzet/Roentgen/issues/34)),
  - `spray_can` ([#30](https://github.com/enzet/Roentgen/issues/30)),
  - `spray_can_spraying` ([#30](https://github.com/enzet/Roentgen/issues/30)),
  - `vending_flower` ([#42](https://github.com/enzet/Roentgen/issues/42)),
  - `vending_pizza` ([#36](https://github.com/enzet/Roentgen/issues/36)).

Redraw icons:
  - `cocktail_glass_with_straw`,
  - `spring` ([#41](https://github.com/enzet/Roentgen/issues/41)),
  - `tree`,
  - `tree___bottom_right_horizontal_line`,
  - `tree___urban_tree_pot`,
  - `tree_with_leaf`,
  - `tree_with_leaf___bottom_right_horizontal_line`,
  - `tree_with_leaf___urban_tree_pot`,
  - `vending_angle`,
  - `vending_bottle`,
  - `vending_bottle_upside_down`,
  - `vending_candles`,
  - `vending_chemist`,
  - `vending_drop`,
  - `vending_machine`,
  - `vending_p`.


## 0.14.0

Add icons:
  - `acorn` ([#28](https://github.com/enzet/Roentgen/issues/28)),
  - `building_bolt_door`,
  - `building_door` ([#24](https://github.com/enzet/Roentgen/issues/24)),
  - `building_drop_door`,
  - `hazelnut`,
  - `hazelnut_with_leaves`,
  - `log_lying` ([#29](https://github.com/enzet/Roentgen/issues/29)),
  - `street_cabinet_bolt`,
  - `street_cabinet_drop`,
  - `vending_bottle_upside_down`,
  - `vending_ice_cream_cone`,
  - `vending_ice_cream_stick`,
  - `water_from_pipe` ([#27](https://github.com/enzet/Roentgen/issues/27)),
  - `wig`,
  - `wig_on_stand` ([#26](https://github.com/enzet/Roentgen/issues/26)).

Redraw icons:
  - `dumbbell`,
  - `street_cabinet`.

To `grid` command add `--match-in` and `--new-in` arguments.


## 0.13.0

Update iconscript version to 0.3.

Add icons:
  - `bicycle___plug`,
  - `double_folded_paper` ([#11](https://github.com/enzet/Roentgen/issues/11)),
  - `power_pole_flag_armless`,
  - `power_tower_barrel_1_level`,
  - `power_tower_donau_1_level`,
  - `power_tower_guyed_v_frame`,
  - `power_tower_h_frame_3_level`,
  - `power_tower_monopolar`,
  - `toilet_bowl`.

Redraw icons:
  - `bicycle`,
  - `bicycle___x_4`,
  - `bicycle___key`,
  - `bicycle___wrench`,
  - `bicycle___p_small`,
  - `cocktail_glass`.

Move `triangle_small` icon.

Add `grid` command for icon grid drawing.


## 0.12.0

Update iconscript version from 0.1 to 0.2 and replace many icons with iconscript
code, instead of SVG files.

Code:
  - Fix `cairosvg` import and encoding error on Windows.

Redraw icons:
  - `envelope`,
  - `i_in_square`,
  - `i`,
  - `pyramid`,
  - `table`,
  - `watches`.

Make icons smoother and make corners round:
  - `table_and_two_chairs___pergola`,
  - `train`.

Fix icons:
  - `greek_cross_in_box`.

Adjust icon size:
  - `survey_point`.


## 0.11.0

Python package:
  - Migrate minimum Python version from 3.9 to 3.10
    ([#8](https://github.com/enzet/Roentgen/issues/8)).
  - Fix `cairosvg` import error on Windows.

Redraw icons:
  - `amusement_ride`,
  - `bicycle_parking_rack`,
  - `bicycle_parking_stand`,
  - `bicycle_parking_wall_loops`,
  - `cctv`,
  - `food_court`,
  - `kiosk`,
  - `marketplace`,
  - `p_small___bicycle_parking_rack`,
  - `p_small___bicycle_parking_stand`,
  - `p_small___bicycle_parking_wall_loops`,
  - `shop_convenience`,
  - `vending_excrement_bag`.

Flip icons:
  - `buffer_stop`,
  - `fountain_roman_wolf`,
  - `supermarket_cart`.


## 0.10.0

Add API for Python package roentgen-icons
([#6](https://github.com/enzet/Roentgen/issues/6)).


## 0.9.0

Add support for iconscript 0.1 files, use iconscript for all `power_tower_*` and
`power_pole_*` icons except for `power_tower_donau`.

Redraw icons:
  - `bed`,
  - `bed_and_roof`,
  - `bed_with_floor_and_ceiling`,
  - `bicycle___wrench`,
  - `car___bed`,
  - `car___wrench`,
  - `coffee_cup`,
  - `fuel_station`,
  - `orbiter`,
  - `peach`,
  - `two_beds`.

Adjust icon size:
  - `cave`,
  - `prison`.

Make icons smoother and make corners round:
  - `charging_station`,
  - `torch`.

Change direction of icons:
  - `wrench`.

Fix icons:
  - `film`,
  - `vending_excrement_bag`.


## 0.8.0

Redraw icons:
  - `bed_and_roof`,
  - `bed_with_floor_and_ceiling`,
  - `bed`,
  - `bollard`,
  - `booster_landing`,
  - `car___bed`,
  - `ear_botany`,
  - `elevator`,
  - `leaf_maple`,
  - `no_wheelchair`,
  - `oat_2`,
  - `oat`,
  - `pillar`,
  - `pole_dancer`,
  - `rocket_flying`,
  - `rocket_on_launch_pad`,
  - `shoe`,
  - `t_shirt`,
  - `torch`,
  - `two_beds`,
  - `tyre`,
  - `wheelchair`,
  - `wood`,
  - `wretch_and_hammer`.

Adjust icon size:
  - `horizontal_ladder`.

Make icons smoother and make corners round:
  - `atm`,
  - `japan_elementary_school`,
  - `shower`.

Fix icon:
  - `microphone`.


## 0.7.0

Redraw icons:
  - `bbq`,
  - `betula___bottom_right_horizontal_line`,
  - `betula___urban_tree_pot`,
  - `betula`,
  - `bicycle___wrench`,
  - `building`,
  - `bush`,
  - `car___wrench`,
  - `coffee_cup`,
  - `diamond`,
  - `drinking_water`,
  - `ear_botany_2`,
  - `fire_pit`,
  - `fireplace`,
  - `fountain_bubbler`,
  - `golf_club_and_ball`,
  - `microphone`,
  - `monument`,
  - `third_stage`,
  - `tooth`,
  - `vending_angle`,
  - `vending_candles`,
  - `vending_drop`,
  - `vending_machine`,
  - `wrench`.

Adjust icon size:
  - `card_and_dice`,
  - `crane_gantry`.

Make icons smoother and make corners round:
  - `bbq`,
  - `beer_mug`,
  - `betula___bottom_right_horizontal_line`,
  - `betula___urban_tree_pot`,
  - `bottle_and_wine_glass`,
  - `bottle`,
  - `city_gate`,
  - `ice_cream`,
  - `ice_cream_2`,
  - `needleleaved_tree___bottom_right_horizontal_line`,
  - `needleleaved_tree___urban_tree_pot`,
  - `obelisk`,
  - `pagoda`,
  - `palm___bottom_right_horizontal_line`,
  - `palm___urban_tree_pot`,
  - `sunflower`,
  - `t_shirt_and_scissors`,
  - `table_and_two_chairs___roof_and_walls`,
  - `tomb`,
  - `tree___bottom_right_horizontal_line`,
  - `tree___urban_tree_pot`,
  - `tree_with_leaf___bottom_right_horizontal_line`,
  - `tree_with_leaf___urban_tree_pot`,
  - `tv`,
  - `vending_bottle`,
  - `vending_chemist`,
  - `woman_and_man`.


## 0.6.0

Reorganize paths of the majority of shapes: delete redundant nodes, simplify
curves. This may change the shape in not detectable way.

Redraw icons:
  - `bag`,
  - `beer_mug`,
  - `books`,
  - `cannon`,
  - `car___car`,
  - `cocktail_glass`,
  - `cocktail_glass_with_straw`,
  - `czech_hedgehog`,
  - `fork_and_knife`,
  - `garage_door`,
  - `government`,
  - `hi_fi`,
  - `rectangle_vertical_rounded_crossed`,
  - `side_mirror`,
  - `slide`,
  - `tyre`.

Make icons smoother and make corners round:
  - `baptist`,
  - `book`,
  - `cactus`,
  - `fort`,
  - `human`,
  - `no_traffic_signals`,
  - `power_generator`,
  - `statue`,
  - `statue_exhibit`,
  - `stop`,
  - `townhall`.

Adjust icon size:
  - `binoculars_on_pole`,
  - `entrance`,
  - `gazette`,
  - `star_of_david`,
  - `stop`,
  - `supermarket_cart`.

Create separate `car___car` icon instead of combination of two `car` icons.


## 0.5.0

Redraw icons:
  - `apple`,
  - `comb_and_scissors`,
  - `digital_clock`,
  - `glasses`,
  - `pear`.

Make icons smoother and make corners round:
  - `at_in_square`,
  - `clockwise`,
  - `counterclockwise`,
  - `cupcake`,
  - `defibrillator`,
  - `fireplace`,
  - `golf_tee`,
  - `japan_castle`,
  - `japan_court`,
  - `japan_fire_station`,
  - `japan_forest_service`,
  - `japan_koban`,
  - `japan_post`,
  - `japan_public_health_center`,
  - `japan_shinto_shrine`,
  - `japan_tv_tower`,
  - `japan_weather_station`,
  - `japan_well`,
  - `money`.

Adjust icon size:
  - `bowling_ball`,
  - `gavel`,
  - `knives`,
  - `watches`.

Flip icons horizontally to make all directed icons be directed to the right.
This changes
  - `bicycle`,
  - `bicycle___key`,
  - `bicycle___p_small`,
  - `bicycle___wrench`,
  - `bicycle___x_4`,
  - `car___key`,
  - `car___wrench`,
  - `dog`,
  - `dog_and_cross`,
  - `massage`,
  - `probe`,
  - `sauna`,
  - `toy_horse`,
  - `wrench`.


## 0.4.0

Redraw icons:
  - `car_on_ferry`,
  - `car`,
  - `caravan`,
  - `ford`,
  - `garages`,
  - `milestone`,
  - `shower_head`,
  - `slide_and_water`.

Redrawing car also changes `car___bed`, `car___car`, `car___key`,
`car___sharing`, `car___shower_head`, and `car___wrench` combinations.

Make icons smoother and make corners round:
  - `cocktail_glass`,
  - `ear_botany`,
  - `golf_pin`,
  - `guidepost`,
  - `memorial`,
  - `survey_point`,
  - `umbrella`.

Making smoother changes `table_and_two_chairs___umbrella` combination.

Enhance script for more popular OpenStreetMap tags.


## 0.3.0

8 June 2025. 514 icons.

Break changes: icons in `icons` directory now have no `roentgen_` prefix.

Redraw icons:
  - `cave`,
  - `knives`,
  - `pole_lamp`,
  - `staircase`.

Make icons smoother and make corners round:
  - `cliff`,
  - `cooling_tower`,
  - `crescent`,
  - `flag`,
  - `gate`,
  - `key`,
  - `plane`,
  - `star_of_david`,
  - `stone`.

Move `bottom_right_horizontal_line` to better fit `tree` and `tree_with_leaf`,
move `building_construction` and slightly change `diving_4_platform`.

Add script for extracting more popular OpenStreetMap tags from Taginfo and
create mapping between OpenStreetMap tags and Röntgen icons.


## 0.2.0

4 June 2025. 514 icons.

Redraw icons:
  - `car_on_ferry`,
  - `gift`,
  - `human_on_ferry`,
  - `seasaw`,
  - `tree_with_leaf`,
  - `tree`.

Make icons smoother and make corners round:
  - `aseptic_carton`,
  - `card_and_dice`,
  - `defensive_tower`,
  - `drawer`,
  - `lock_unlocked`,
  - `medicine_bottle`,
  - `needleleaved_tree`,
  - `palm`,
  - `sheets`,
  - `solar_panel`,
  - `supermarket_cart`,
  - `taxi`,
  - `waterfall`.

Changes on trees also influence their combinations with
`bottom_right_horizontal_line` and `urban_tree_pot`.

Unify style for water in different icons:
  - `car_on_ferry`,
  - `crane_travel_lift`,
  - `human_on_ferry`,
  - `waterfall`.


## 0.1.0

29 August 2023. This is the first version after migrating the Röntgen project
from the Map Machine repository to its own repository. This version contains 514
icons, including icon combinations.

This is the first version used in the iD editor. The icons were copied to the
[`svg/roentgen`](https://github.com/openstreetmap/iD/tree/develop/svg/roentgen)
directory by
[this commit](https://github.com/openstreetmap/iD/commit/98e9a11a511179b24c8c0aa6f520a9ed372b1c55).


Added 514 icons:
  `advertising_column`,
  `amphora`,
  `amusement_ride`,
  `anchor`,
  `apartments_1_story`,
  `apartments_1_story_gabled_roof`,
  `apartments_1_story_skillion_roof`,
  `apartments_2_story`,
  `apartments_2_story_gabled_roof`,
  `apartments_2_story_skillion_roof`,
  `apartments_3_story`,
  `apartments_3_story_gabled_roof`,
  `apartments_3_story_skillion_roof`,
  `apartments_4_story`,
  `apartments_4_story_gabled_roof`,
  `apartments_4_story_skillion_roof`,
  `apartments_5_story`,
  `apartments_5_story_gabled_roof`,
  `apartments_5_story_skillion_roof`,
  `apple`,
  `aseptic_carton`,
  `at_in_square`,
  `atm`,
  `bag`,
  `bag_with_percent`,
  `baptist`,
  `bbq`,
  `beach`,
  `bed`,
  `bed_and_roof`,
  `bed_with_floor_and_ceiling`,
  `beer_mug`,
  `bench`,
  `bench_backrest`,
  `bench_no_backrest`,
  `bench_with_inscription`,
  `bench_with_shelter`,
  `bench_with_statue`,
  `betula`,
  `betula___bottom_right_horizontal_line`,
  `betula___urban_tree_pot`,
  `bicycle`,
  `bicycle___key`,
  `bicycle___p_small`,
  `bicycle___wrench`,
  `bicycle___x_4`,
  `bicycle_parking_rack`,
  `bicycle_parking_stand`,
  `bicycle_parking_wall_loops`,
  `billboard`,
  `binoculars`,
  `binoculars_on_pole`,
  `bleachers`,
  `block`,
  `bollard`,
  `book`,
  `books`,
  `booster_landing`,
  `bottle`,
  `bottle_and_wine_glass`,
  `bowling_ball`,
  `bricks`,
  `briefcase`,
  `buffer_stop`,
  `building`,
  `building_construction`,
  `building_container`,
  `bump`,
  `buoy`,
  `burger`,
  `bus`,
  `bus_stop`,
  `bus_stop_sign`,
  `bus_stop_sign___bus_stop_bench`,
  `bus_stop_sign___bus_stop_bench___bus_stop_shelter`,
  `bus_stop_sign___bus_stop_bench___platform___bus_stop_shelter`,
  `bus_stop_sign___bus_stop_shelter`,
  `bus_stop_sign___platform___bus_stop_bench`,
  `bus_stop_sign___platform___bus_stop_shelter`,
  `buses`,
  `bush`,
  `cactus`,
  `camp`,
  `cannon`,
  `car`,
  `car___bed`,
  `car___car`,
  `car___key`,
  `car___sharing`,
  `car___shower_head`,
  `car___wrench`,
  `car_on_ferry`,
  `caravan`,
  `card_and_dice`,
  `cave`,
  `cctv`,
  `cctv_dome_ceiling`,
  `cctv_dome_wall`,
  `chain_barrier`,
  `charging_station`,
  `chimney`,
  `christmas_tree`,
  `circle_11`,
  `circle_3`,
  `circle_4`,
  `circle_9`,
  `circle_empty`,
  `city_gate`,
  `city_limit_sign`,
  `cliff`,
  `clock`,
  `clock___support_column`,
  `clock___support_pole`,
  `clock___support_wall`,
  `clockwise`,
  `cocktail_glass`,
  `cocktail_glass_with_straw`,
  `coffee_cup`,
  `comb_and_scissors`,
  `connector_chademo`,
  `connector_schuko`,
  `connector_tesla`,
  `connector_type_1`,
  `connector_type_2`,
  `connector_type_e`,
  `counterclockwise`,
  `crane`,
  `crane_gantry`,
  `crane_portal`,
  `crane_travel_lift`,
  `crater`,
  `credit_card`,
  `crescent`,
  `cross_and_horizontal_bar`,
  `crossing`,
  `cupcake`,
  `curtains`,
  `czech_hedgehog`,
  `default`,
  `default_small`,
  `defibrillator`,
  `descent_stage`,
  `dharmachakra`,
  `diamond`,
  `digital_clock`,
  `dip`,
  `diving_1_platforms`,
  `diving_2_platforms`,
  `diving_3_platforms`,
  `diving_4_platforms`,
  `dog`,
  `dog_and_cross`,
  `dollar`,
  `door_with_keyhole`,
  `double_dip`,
  `dragons_teeth`,
  `drawer`,
  `drinking_water`,
  `dumbbell`,
  `ear_botany`,
  `ear_botany_2`,
  `electricity`,
  `elevator`,
  `engine`,
  `entrance`,
  `envelope`,
  `exchange`,
  `exchange___dollar___pound`,
  `exit`,
  `film`,
  `fire_extinguisher`,
  `fire_hydrant`,
  `fire_pit`,
  `fireplace`,
  `fishing_angle`,
  `flag_bend_sinister`,
  `flag_triangle_flanche`,
  `flag_usa`,
  `flag_vertical_triband`,
  `flagpole`,
  `flower_in_pot`,
  `food_court`,
  `foot`,
  `ford`,
  `fork_and_knife`,
  `fort`,
  `fountain`,
  `fountain_bubbler`,
  `fountain_cascade`,
  `fountain_roman_wolf`,
  `fountain_toret`,
  `frame`,
  `free`,
  `fuel_station`,
  `garage_door`,
  `garages`,
  `gate`,
  `gavel`,
  `gazette`,
  `gift`,
  `glasses`,
  `glider`,
  `globe`,
  `golf_club_and_ball`,
  `golf_pin`,
  `golf_tee`,
  `government`,
  `grapes`,
  `grapes_2`,
  `grapes_3`,
  `greek_cross`,
  `greek_cross_in_box`,
  `guidepost`,
  `h`,
  `hanger`,
  `hi_fi`,
  `historic`,
  `hopscotch`,
  `horizontal_bar`,
  `horizontal_ladder`,
  `houseboat`,
  `human`,
  `human_on_ferry`,
  `hump`,
  `hunting_stand`,
  `i`,
  `i_in_square`,
  `i_in_square___support_column`,
  `i_in_square___support_pole`,
  `i_in_square___support_wall`,
  `ice_cream`,
  `ice_cream_2`,
  `japan_castle`,
  `japan_court`,
  `japan_elementary_school`,
  `japan_fire_station`,
  `japan_forest_service`,
  `japan_historic`,
  `japan_koban`,
  `japan_police_station`,
  `japan_post`,
  `japan_public_health_center`,
  `japan_shinto_shrine`,
  `japan_tv_tower`,
  `japan_weather_station`,
  `japan_well`,
  `kerb`,
  `kiosk`,
  `knives`,
  `lander`,
  `latin_cross`,
  `lattice`,
  `lattice___dish_antenna_left___dish_antenna_right`,
  `lattice___light_left___light_right`,
  `lattice___siren_left___siren_right`,
  `lattice___wave_left___wave_right`,
  `lattice_guyed`,
  `lattice_guyed___dish_antenna_left___dish_antenna_right`,
  `lattice_guyed___light_left___light_right`,
  `lattice_guyed___siren_left___siren_right`,
  `lattice_guyed___wave_left___wave_right`,
  `leaf_maple`,
  `life_ring`,
  `lift_gate`,
  `lock`,
  `lock_unlocked`,
  `lock_with_keyhole`,
  `low_horizontal_bars`,
  `lowered_kerb`,
  `lunokhod`,
  `maglev`,
  `main_entrance`,
  `manhole_drain`,
  `marketplace`,
  `massage`,
  `mausoleum`,
  `maze`,
  `maze___arrow_right_short`,
  `medicine_bottle`,
  `memorial`,
  `microphone`,
  `milestone`,
  `minaret`,
  `mini_bumps`,
  `money`,
  `monorail`,
  `monument`,
  `needleleaved_tree`,
  `needleleaved_tree___bottom_right_horizontal_line`,
  `needleleaved_tree___urban_tree_pot`,
  `no_door`,
  `no_foot`,
  `no_traffic_signals`,
  `no_wheelchair`,
  `oat`,
  `oat_2`,
  `obelisk`,
  `observatory`,
  `onion_roof_shape`,
  `orbiter`,
  `orthodox`,
  `p`,
  `p___arrow_down`,
  `p___arrow_right`,
  `p___arrow_up`,
  `p_small`,
  `p_small___bicycle_parking_rack`,
  `p_small___bicycle_parking_stand`,
  `p_small___bicycle_parking_wall_loops`,
  `pac_man`,
  `pagoda`,
  `palm`,
  `palm___bottom_right_horizontal_line`,
  `palm___urban_tree_pot`,
  `pan`,
  `peach`,
  `pear`,
  `phone`,
  `photo_camera`,
  `picture`,
  `pillar`,
  `pipeline`,
  `plane`,
  `plaque`,
  `pole`,
  `pole_dancer`,
  `pole_lamp`,
  `pound`,
  `power_generator`,
  `power_pole_1_level`,
  `power_pole_2_level`,
  `power_pole_3_level`,
  `power_pole_4_level`,
  `power_pole_asymmetric`,
  `power_pole_asymmetric_armless`,
  `power_pole_delta`,
  `power_pole_flag`,
  `power_pole_triangle`,
  `power_pole_triangle_armless`,
  `power_tower_1_level`,
  `power_tower_2_level`,
  `power_tower_3_level`,
  `power_tower_4_level`,
  `power_tower_asymmetric`,
  `power_tower_barrel`,
  `power_tower_delta`,
  `power_tower_delta_2_level`,
  `power_tower_delta_3_level`,
  `power_tower_donau`,
  `power_tower_donau_inverse`,
  `power_tower_flag`,
  `power_tower_guyed_h_frame`,
  `power_tower_h_frame`,
  `power_tower_h_frame_2_level`,
  `power_tower_portal`,
  `power_tower_portal_2_level`,
  `power_tower_portal_3_level`,
  `power_tower_triangle`,
  `power_tower_x_frame`,
  `power_tower_y_frame`,
  `prison`,
  `probe`,
  `pyramid`,
  `rape`,
  `rape_2`,
  `rectangle_vertical_rounded`,
  `rectangle_vertical_rounded_crossed`,
  `recycling_container`,
  `rings`,
  `rocket_flying`,
  `rocket_on_launch_pad`,
  `roundabout`,
  `rumble_strip`,
  `russian_orthodox_cross`,
  `saddle`,
  `sandpit`,
  `sauna`,
  `seesaw`,
  `sharing`,
  `sheets`,
  `shelter`,
  `shield_volcano`,
  `shield_volcano___lava`,
  `shield_volcano___smoke`,
  `shield_volcano___smoke_2`,
  `shoe`,
  `shop_convenience`,
  `shower`,
  `side_mirror`,
  `signal`,
  `sit_up`,
  `skateboard`,
  `slide`,
  `slide_and_water`,
  `solar_panel`,
  `sos_phone`,
  `spring`,
  `stained_glass`,
  `staircase`,
  `star_of_david`,
  `statue`,
  `statue_exhibit`,
  `steak_and_fork`,
  `stone`,
  `stone_with_inscription`,
  `stop`,
  `stratovolcano`,
  `stratovolcano___lava`,
  `stratovolcano___smoke`,
  `stratovolcano___smoke_2`,
  `street_cabinet`,
  `street_lamp`,
  `stupa`,
  `sunflower`,
  `supermarket_cart`,
  `survey_point`,
  `suspension_railway`,
  `swimming_area`,
  `t`,
  `t_shirt`,
  `t_shirt_and_scissors`,
  `table`,
  `table_and_two_chairs`,
  `table_and_two_chairs___awning`,
  `table_and_two_chairs___pergola`,
  `table_and_two_chairs___roof`,
  `table_and_two_chairs___roof_and_walls`,
  `table_and_two_chairs___umbrella`,
  `tactile_paving`,
  `tactile_paving___x_5`,
  `taxi`,
  `telephone`,
  `telescope_gamma`,
  `telescope_radio`,
  `third_stage`,
  `ticket`,
  `toll_booth`,
  `tomb`,
  `tooth`,
  `torch`,
  `toucan_crossing`,
  `tower`,
  `tower_communication`,
  `tower_cooling`,
  `tower_defensive`,
  `tower_observation`,
  `townhall`,
  `toy_horse`,
  `traffic_cushion`,
  `traffic_signals`,
  `traffic_table`,
  `train`,
  `tram`,
  `transformer`,
  `tree`,
  `tree___bottom_right_horizontal_line`,
  `tree___urban_tree_pot`,
  `tree_with_leaf`,
  `tree_with_leaf___bottom_right_horizontal_line`,
  `tree_with_leaf___urban_tree_pot`,
  `triangle_down_hollow`,
  `triangle_small`,
  `trolleybus`,
  `tube`,
  `tube___dish_antenna_left___dish_antenna_right`,
  `tube___light_left___light_right`,
  `tube___siren_left___siren_right`,
  `tube___wave_left___wave_right`,
  `tube_guyed`,
  `tube_guyed___dish_antenna_left___dish_antenna_right`,
  `tube_guyed___light_left___light_right`,
  `tube_guyed___siren_left___siren_right`,
  `tube_guyed___wave_left___wave_right`,
  `turning_loop`,
  `turnstile`,
  `tv`,
  `two_beds`,
  `two_people_together`,
  `tyre`,
  `vanity_mirror`,
  `vending_angle`,
  `vending_bottle`,
  `vending_candles`,
  `vending_chemist`,
  `vending_drop`,
  `vending_excrement_bag`,
  `vending_machine`,
  `vending_p`,
  `vending_tickets`,
  `ventilation`,
  `volcanic_cone`,
  `volcanic_cone___lava`,
  `volcanic_cone___smoke`,
  `volcanic_cone___smoke_2`,
  `wall_bars`,
  `washing_machine`,
  `waste_basket`,
  `waste_disposal`,
  `watches`,
  `waterfall`,
  `waving_flag`,
  `wayside_shrine`,
  `wheelchair`,
  `wind_turbine`,
  `wlan`,
  `wlan___free`,
  `woman_and_man`,
  `wood`,
  `wrench`,
  `wretch_and_hammer`,
  `x`,
  `x_4`,
  `x_5`,
  `y`.