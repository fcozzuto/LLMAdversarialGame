def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs_list = observation.get("obstacles") or []
    obs = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "pursuer")).lower()
    is_evader = (role == "evader")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def near_obstacle_pen(x, y):
        # Strong repulsion if landing on obstacle (should already be blocked), mild near penalty.
        if (x, y) in obs:
            return 10**9
        pen = 0
        for ax, ay in obs:
            d = abs(x - ax) + abs(y - ay)
            if d == 0:
                return 10**9
            if d == 1:
                pen += 7
            elif d == 2:
                pen += 3
            elif d == 3:
                pen += 1
        return pen

    # Center-pinning target: constrain zigzag by pushing toward the side of the opponent
    # relative to the grid center.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    side_x = 1 if ox > cx else (-1 if ox < cx else 0)
    side_y = 1 if oy > cy else (-1 if oy < cy else 0)
    if side_x == 0:
        side_x = 1 if sx < ox else -1
    if side_y == 0:
        side_y = 1 if sy < oy else -1
    pin_target = (ox + side_x * 1, oy + side_y * 1)

    best_score = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        d_pin = dist2(nx, ny, pin_target[0], pin_target[1])
        align = abs((nx - ox)) + abs((ny - oy))
        step_cost = (dx != 0 or dy != 0)

        # Pursuer: minimize distance; Evader: maximize distance.
        # Add "pin" term so pursuer approaches a likely interception neighborhood.
        if is_evader:
            score = d_opp - 0.4 * d_pin + 0.05 * align + 0.8 * near_obstacle_pen(nx, ny) + 0.01 * step_cost
            better = (best_score is None) or (score > best_score)
        else:
            score = d_opp + 0.35 * d_pin + 0.15 * align + 1.2 * near_obstacle_pen(nx, ny) + 0.01 * step_cost
            better = (best_score is None) or (score < best_score)

        if better:
            best_score = score
            best_move = [dx, dy]

    return best_move