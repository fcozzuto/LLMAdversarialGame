def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if resources:
        best = None
        for rx, ry in resources:
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # Prefer resources where we are closer; break ties by larger advantage and then by position.
            score = (do - ds, -ds, -rx, -ry)
            if best is None or score > best[0]:
                best = (score, (rx, ry))
        tx, ty = best[1]
        best_move = (0, 0)
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            # Primary: reduce our distance to target. Secondary: increase opponent distance.
            ns = dist((nx, ny), (tx, ty))
            no = dist((nx, ny), (ox, oy))  # discourage chasing opponent directly; still used as tiebreak
            opp_to_target = dist((ox, oy), (tx, ty))
            val = (-ns, opp_to_target, -no, dx, dy)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: go toward center while avoiding obstacles
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        val = (-dist((nx, ny), (cx, cy)), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]