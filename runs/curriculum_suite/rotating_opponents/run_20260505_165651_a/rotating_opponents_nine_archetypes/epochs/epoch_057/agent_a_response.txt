def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obstacles)
    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    # No resources: drift to center while staying away from opponent
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny): 
                continue
            key = (man(nx, ny, cx, cy), -man(nx, ny, ox, oy), dx, dy)
            if best is None or key < best:
                best, best_move = key, [dx, dy]
        return best_move

    # Choose target resource: reach-first, then contest based on opponent distance
    best_res = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        cx, cy = (w - 1) // 2, (h - 1) // 2
        center = man(rx, ry, cx, cy)
        key = (sd, -od, center, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)
    rx, ry = best_res

    # Move greedily toward target with deterministic obstacle avoidance; otherwise gain separation
    desired_dx = 0 if rx == sx else (1 if rx > sx else -1)
    desired_dy = 0 if ry == sy else (1 if ry > sy else -1)
    prefer = (desired_dx, desired_dy)

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        to_target = man(nx, ny, rx, ry)
        sep = man(nx, ny, ox, oy)
        # primary: get closer; secondary: keep away from opponent; tertiary: align with desired move
        align = 0 if (dx, dy) == prefer else 1
        key = (to_target, -sep, align, dx, dy)
        if best is None or key < best:
            best, best_move = key, [dx, dy]
    return best_move