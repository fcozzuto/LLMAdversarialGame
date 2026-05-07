def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    res = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not res:
        # deterministic fallback: move toward opponent corner-side resourceless
        tx = 0 if (sy + sx) % 2 else gw - 1
        ty = 0 if (sy + sx) % 3 else gh - 1
        bx, by = sx, sy
        step_x = 1 if tx > sx else -1 if tx < sx else 0
        step_y = 1 if ty > sy else -1 if ty < sy else 0
        nx, ny = bx + step_x, by + step_y
        return [step_x if legal(nx, ny) else (1 if legal(bx + step_x, by) and step_x != 0 else -1 if legal(bx - step_x, by) and step_x != 0 else 0),
                step_y if legal(nx, ny) else (1 if legal(bx, by + step_y) and step_y != 0 else -1 if legal(bx, by - step_y) and step_y != 0 else 0)]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # If we can take a resource this turn, heavily prefer it
        take = 1 if (nx, ny) in obstacles else 0
        # Score based on race (how much closer we are than opponent to resources)
        worst_opp = 10**9
        best_race = -10**18
        nearest_me = 10**9
        nearest_opp = 10**9

        for rx, ry in res:
            my_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            if my_d < nearest_me:
                nearest_me = my_d
            if opp_d < nearest_opp:
                nearest_opp = opp_d
            race = opp_d - my_d
            if race > best_race:
                best_race = race
            if my_d == 0:
                best_race = 10**6
                nearest_me = 0
                break
            if opp_d < worst_opp:
                worst_opp = opp_d

        # Encourage blocking/denial when opponent is closer (negative race)
        # Also prefer reducing our distance to nearest resource.
        val = 0
        val += best_race * 30
        if nearest_me == 0:
            val += 10**7
        val += (gw + gh - nearest_me) * 2
        val -= max(0, nearest_opp - nearest_me) * 3
        # Tiny deterministic bias to break ties: favor moves with smaller dx, then dy
        val -= (abs(dx) * 0.01 + abs(dy) * 0.001)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]