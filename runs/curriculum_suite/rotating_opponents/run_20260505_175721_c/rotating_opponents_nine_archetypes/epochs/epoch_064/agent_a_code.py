def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    # Identify opponent's most attractive resource (nearest by Manhattan)
    opp_best = None
    opp_best_d = None
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if opp_best_d is None or d < opp_best_d or (d == opp_best_d and (rx, ry) < opp_best):
            opp_best_d = d
            opp_best = (rx, ry)

    # Choose a resource where we are relatively better (opp farther than us), avoid taking opponent's best if possible
    best = None
    best_key = None
    for rx, ry in resources:
        our_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        # Prefer resources that are "ours to take": minimize (our_d - opp_d); tie-break by our_d
        key = (our_d - opp_d, our_d, rx, ry)
        if opp_best is not None and (rx, ry) == opp_best:
            key = (key[0] + 2, key[1], key[2], key[3])  # small penalty to avoid direct contest
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If that target step is blocked, try alternative greedy directions
    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    # Deterministic ordering for diagonals when needed
    if dx != 0 and dy != 0:
        candidates = [(dx, dy), (dx, -dy), (-dx, dy), (0, dy), (dx, 0), (0, 0)]
    seen = set()
    for m in candidates:
        if m in seen:
            continue
        seen.add(m)
        mx, my = m
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(mx), int(my)]

    # Fallback: find any legal move that doesn't step onto an obstacle
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [int(mx), int(my)]
    return [0, 0]