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

    def near_obstacle_penalty(x, y):
        # small deterministic deterrent to prevent repeated obstacle bumps
        p = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                p += 1
        return p

    if not res:
        # fallback: move to center-ish while avoiding obstacles
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -dist(nx, ny, cx, cy) - near_obstacle_penalty(nx, ny) * 2
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Race-first: prioritize resources where we are (and remain) closer than the opponent
    best_move = (0, 0)
    best_val = -10**18
    remain = observation.get("remaining_resource_count", len(res)) or len(res)
    race_weight = 10 + (12 if remain <= len(res) // 2 else 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_here_opp = dist(nx, ny, ox, oy)  # encourages positioning that keeps pressure
        my_best_race = -10**18
        my_best_dist = 10**9
        for rx, ry in res:
            my_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            race = opp_d - my_d
            # Big reward for taking a lead; small penalty for longer travel; slight bias to immediate collection
            s = race_weight * race - my_d + (1 if (nx, ny) == (rx, ry) else 0)
            if s > my_best_race or (s == my_best_race and my_d < my_best_dist):
                my_best_race = s
                my_best_dist = my_d
        # tie-break positioning: if race tie, move closer to opponent (to block) and avoid obstacles
        val = my_best_race + (2 if remain <= 4 else 0) * (my_here_opp == 0) - my_here_opp * 0.1 - near_obstacle_penalty(nx, ny) * 2
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]