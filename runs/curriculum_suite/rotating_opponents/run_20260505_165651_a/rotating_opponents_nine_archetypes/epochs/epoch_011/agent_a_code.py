def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_t = None
    best_score = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        dist_center = abs(rx - cx) + abs(ry - cy)
        # Try to win races: reward where we are closer, but keep some greed against far targets.
        score = (od - sd) + (1.0 / (sd + 1)) + 0.15 * (dist_center == 0) - 0.01 * dist_center
        if best_score is None or score > best_score or (score == best_score and (rx, ry) < best_t):
            best_score = score
            best_t = (rx, ry)

    rx, ry = best_t
    cur_my = man(sx, sy, rx, ry)
    cur_opp = man(ox, oy, rx, ry)

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        my_next = man(nx, ny, rx, ry)
        opp_next = man(ox, oy, rx, ry)
        # Move evaluation: decrease our distance, avoid giving opponent advantage.
        val = 2.0 * (cur_my - my_next) + 0.9 * (opp_next - my_next) + (1.0 / (my_next + 1))
        # If our next position is in/near the resource, strongly prefer.
        if my_next == 0:
            val += 100.0
        # Small deterministic bias to avoid oscillations: prefer increasing towards target x,y then staying.
        if dx != 0 and rx != sx:
            val += 0.02 * (1 if (dx == 1 and rx > sx) or (dx == -1 and rx < sx) else 0)
        if dy != 0 and ry != sy:
            val += 0.02 * (1 if (dy == 1 and ry > sy) or (dy == -1 and ry < sy) else 0)

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]