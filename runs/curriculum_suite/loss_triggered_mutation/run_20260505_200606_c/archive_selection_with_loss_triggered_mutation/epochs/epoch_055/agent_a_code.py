def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = (0, 0)

    # If no resources are visible, drift toward center to reduce opponent reach later.
    if not resources:
        tx = (w - 1) // 2
        ty = (h - 1) // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if inb(nx, ny) and (nx, ny) not in obstacles:
                if mx == dx or my == dy:
                    return [mx, my]
        return [0, 0]

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Key: maximize our lead (opp_dist - self_dist). If we can't lead, minimize opp distance (deny).
        # Deterministic tie breaks: prefer closer to resource, then resource coordinates, then move order.
        local = None
        for rx, ry in resources:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            key = (od - sd, -od, -sd, -rx, -ry)  # prefer lead, then reduce opponent distance, then self closeness
            if local is None or key > local:
                local = key
        if local is None:
            continue

        # Slight preference for staying away from obstacles corners: keep movement minimal if equivalent.
        step_pen = abs(mx) + abs(my)
        key2 = (local[0], local[1], local[2], local[3], local[4], -step_pen, mx, my)
        if best is None or key2 > best:
            best = key2
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]