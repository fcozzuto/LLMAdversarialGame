def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except:
            pass

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    self_role = str(observation.get("self_role", "") or "").lower()
    opponent_role = str(observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("evad" in opponent_role) or ("hunter" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = None

    # Precompute nearest obstacle distance (cheapest local measure)
    obs_list = list(obstacles)
    def nearest_obs_dist(x, y):
        if not obs_list:
            return 99
        dmin = 99
        for (bx, by) in obs_list:
            d = abs(x - bx) + abs(y - by)
            if d < dmin:
                dmin = d
                if dmin == 0:
                    break
        return dmin

    for dx, dy in moves:
        nx, ny = int(sx) + dx, int(sy) + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        dist = md(nx, ny, int(ox), int(oy))
        nob = nearest_obs_dist(nx, ny)

        if is_pursuer:
            # chase opponent, avoid obstacles, prefer smaller distance
            val = (-dist * 1000) + (nob * 5) - (abs(dx) + abs(dy)) * 0.01
        else:
            # evade opponent, avoid obstacles, prefer larger distance
            val = (dist * 1000) + (nob * 5) - (abs(dx) + abs(dy)) * 0.01

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
        elif val == best_val:
            # deterministic tie-breaker: smallest dx, then dy
            if dx < best_move[0] or (dx == best_move[0] and dy < best_move[1]):
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]