def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    turns = observation.get("turns_remaining", 0)
    greedy_phase = turns <= 10 or observation.get("remaining_resource_count", 999) <= 4

    best = None
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if greedy_phase:
            score = (-ds, rx, ry)
        else:
            # Intercept: prioritize being earlier, and if close, make it attractive to us but hard for opponent.
            lead = do - ds  # positive means we are closer in time-to-reach
            score = (lead, -ds, -do, rx, ry)
        if best is None or score > best[0]:
            best = (score, rx, ry)

    if best is None:
        return [0, 0]
    _, tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (-dx, -dy), (-dx, 0), (0, -dy), (0, 0)]
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            return [int(mx), int(my)]
    return [0, 0]