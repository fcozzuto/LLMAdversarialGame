def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_key = None

    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Opponent is sweep_rows: contest most likely when resource is on (or near) opponent row.
        row_contest = -abs(ry - oy)  # prefer farther from opponent row
        # Primary objective: be earlier / have advantage.
        adv = od - sd
        # Secondary: prefer shorter own distance (less wandering) and avoid very close dead-even spots.
        key = (adv, row_contest, -sd, -abs(rx - sx))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry, sd, od)

    if best is None:
        # No reachable resources: step away from opponent in the strongest direction.
        tx = sx + (-1 if ox > sx else (1 if ox < sx else 0))
        ty = sy + (-1 if oy > sy else (1 if oy < sy else 0))
        tx = min(w - 1, max(0, tx))
        ty = min(h - 1, max(0, ty))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    rx, ry, sd, od = best

    # If we're not strictly advantaged, break tie by moving to safer row (less sweep-row contention).
    if od <= sd:
        # Try same-sign move towards a resource row that maximizes row separation deterministically.
        best2 = None
        best2_key = None
        for px, py in resources:
            if not inb(px, py) or (px, py) in obstacles:
                continue
            if man(sx, sy, px, py) > sd + 2:
                continue
            sep = abs(py - oy)
            k2 = (sep, -(man(ox, oy, px, py)), -man(sx, sy, px, py))
            if best2_key is None or k2 > best2_key:
                best2_key = k2
                best2 = (px, py)
        if best2 is not None:
            rx, ry = best2

    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)
    return [dx, dy]