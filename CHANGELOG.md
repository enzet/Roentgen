## Unreleased

Reorganize paths of the majority of shapes: delete redundant nodes, simplify
curves. This may change the shape in not detectable way.

Redraw icons:
  - `beer_mug`,
  - `garage_door`,
  - `government`,
  - `hi_fi`,
  - `side_mirror`,
  - `slide`,

Make icons smoother and make corners round:
  - `cactus`,
  - `fort`,
  - `no_traffic_signals`,
  - `stop`,
  - `townhall`.

Adjust icon size:
  - `stop`,
  - `supermarket_cart`.

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
