def choose_move(observation):
    turn_index = observation.get("turn_index", 0)
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1), (0,-1), (1,-1),
              (-1, 0), (0,0), (1,0),
              (-1,1), (0,1), (1,1)]

    valid = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    resources = [tuple(r) for r in observation.get("resources", [])]
    if resources:
        # choose resource that is closest to me and far from opponent
        best = None
        best_score = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_me = abs(rx - sx) + abs(ry - sy)
            d_opp = abs(rx - ox) + abs(ry - oy)
            score = (d_opp - d_me)
            if best_score is None or score > best_score:
                best_score = score
                best = (rx, ry)
        target = best if best is not None else (w//2, h//2)
    else:
        target = (w//2, h//2)

    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    best_dxdy = valid[0]
    best_val = -10**9
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        dist_to_target = man((nx, ny), target)
        dist_opponent = man((ox, oy), target)
        # Prefer moves that bring us closer to target while keeping safe from opponent
        val = -dist_to_target - dist_opponent*0  # encourage closeness to target
        # tie-breaker: prefer moves that increase distance from opponent if same distance to target
        if dist_to_target == 0:
            val += 5
        if val > best_val:
            best_val = val
            best_dxdy = (dx, dy)

    return [best_dxdy[0], best_dxdy[1]]