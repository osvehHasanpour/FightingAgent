#include <exception>
#include <iostream>
#include <string>
#include <ctime>


#include "./json.hpp"

using json = nlohmann::json;
using namespace std;



json make_move(const json& fighter_info, const json& opponent_info, json& saved_data) {
  json action;
  action["move"] = nullptr;
  action["attack"] = nullptr;
  action["jump"] = false;
  action["dash"] = nullptr;
  action["debug"] = nullptr;
  //by default keep the previous saved_data
  action["saved_data"] = saved_data;




  //examples of how to use saved_data

  // if (saved_data["last_action"].is_null()) {
  //   saved_data["last_action"] = 0;
  // }
  // else {
  //   saved_data["last_action"] = (saved_data["last_action"].get<int>() + 1) % 100;
  // }

  // action["debug"] = saved_data["last_action"];

  // int current;
  // try{
  //   current = saved_data["last_action"].get<int>();

  // }catch (const exception& e) {
  //   current = 0;
  // }
  // saved_data["last_action"] = (current + 1);


  //attack cooldowns
  vector<int> attack_cooldowns = fighter_info["attack_cooldown"].get<vector<int>>();
  int light_attack_cooldown = attack_cooldowns[0];
  int heavy_attack_cooldown = attack_cooldowns[1];


  //are we attacking right now
  bool is_attacking = fighter_info["attacking"].get<bool>();

  //dash cooldown in frames
  int dash_cooldown = fighter_info["dash_cooldown"].get<int>();

  //current health
  int fighterHealth = fighter_info["health"].get<int>();

  //are we jumping right now
  bool is_jumping = fighter_info["jump"].get<bool>();

  //our coordinates
  int fighter_x = fighter_info["x"].get<int>();
  int fighter_y = fighter_info["y"].get<int>();


  //opponent coordinates
  int opponent_x = opponent_info["x"].get<int>();
  int opponent_y = opponent_info["y"].get<int>();

  //opponent health
  int opponentHealth = opponent_info["health"].get<int>();

  //opponent is attacking
  bool opponent_is_attacking = opponent_info["attacking"].get<bool>();


  //your desicios here




  return action;
}

int main() {
  // Read input JSON from stdin
  string input;
  getline(cin, input);

  try {
    json data = json::parse(input);
    json fighter_info = data["fighter"];
    json opponent_info = data["opponent"];
    json saved_data = data["saved_data"];

    // Get move decision
    json move = make_move(fighter_info, opponent_info,saved_data);

    // Output the move as JSON
    cout << move.dump() << endl;
  } catch (const exception& e) {
    cerr << "Error: " << e.what() << endl;
    json default_move;
    default_move["move"] = nullptr;
    default_move["attack"] = nullptr;
    default_move["jump"] = false;
    default_move["dash"] = nullptr;
    cout << default_move.dump() << endl;
  }

  return 0;
}
