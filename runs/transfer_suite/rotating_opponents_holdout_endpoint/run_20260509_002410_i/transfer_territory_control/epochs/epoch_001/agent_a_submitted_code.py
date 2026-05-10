def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = set(obstacles)
    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    resources = observation.get("resources", []) or []
    best_resource = None
    best_rd = 10**9
    for rx, ry in resources:
        d = abs(sx - rx) + abs(sy - ry)
        if d < best_rd:
            best_rd = d
            best_resource = (rx, ry)

    score_self = observation.get("scores", {}).get("self", observation.get("scores", {}).get("me", 0))
    score_opp = observation.get("scores", {}).get("opponent", observation.get("scores", {}).get("them", 0))
    behind = score_self <= score_opp

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_res = 0
        if best_resource is not None:
            d_res = abs(nx - best_resource[0]) + abs(ny - best_resource[1])
        # Attack if behind (try to approach), otherwise balance: approach resources and keep distance.
        val = 0
        if d_opp == 0:
            val += 1000000
        if d_opp <= 1:
            val += 5000 if behind else 2000
        if behind:
            val += -d_opp * 20
        else:
            val += d_opp * 5
        val += -d_res * 3
        # Prefer moving (avoid staying unless it's best)
        if dx == 0 and dy == 0:
            val -= 1
        # Deterministic tie-breaker: fixed ordering already ensures stability; still compare strictly
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]