def choose_move(observation):
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if resources:
        pass
    else:
        resources = []
    def steps(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    best_t = None
    best_score = -10**18
    for rx, ry in resources:
        st = steps((sx, sy), (rx, ry))
        ot = steps((ox, oy), (rx, ry))
        # Prefer resources we can reach sooner; penalize contested ones.
        lead = ot - st
        # Also prefer closer overall resources to secure.
        value = (lead * 100) - (st * 3) + (0 if (rx+ry) % 2 == (sx+sy) % 2 else -1)
        # If no lead, still allow but less.
        if lead <= 0:
            value -= (abs(lead) * 20) + st
        if value > best_score:
            best_score = value
            best_t = (rx, ry)
    tx, ty = (sx, sy) if not best_t else best_t
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def objective(nx, ny):
        if (nx, ny) in obstacles:
            return -10**15
        # Move toward target
        cur_st = steps((nx, ny), (tx, ty))
        cur_ot = steps((ox, oy), (tx, ty))
        lead = cur_ot - cur_st
        score = (lead * 100) - (cur_st * 3)
        # Discourage moving into opponent's immediate reach
        opp_reach = steps((nx, ny), (ox, oy))
        score -= max(0, 2 - opp_reach) * 25
        return score
    best_move = (0, 0)
    best_obj = -10**18
    # Deterministic tie-breaker: prefer smaller dx, then smaller dy, then (0,0) bias last
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        obj = objective(nx, ny)
        if obj > best_obj:
            best_obj = obj
            best_move = (dx, dy)
        elif obj == best_obj:
            if (dx, dy) < best_move:
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]