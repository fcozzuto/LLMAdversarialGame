def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    evade = ("evader" in role) or ("runner" in role) or ("evasion" in role) or ("evasive" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Evade: go to farthest corner from opponent, obstacle-aware.
    # Pursue: chase opponent (or its nearest corner if path is poor).
    if evade:
        target = corners[0]
        bestd = -1
        for cx, cy in corners:
            d = man(cx, cy, ox, oy)
            if d > bestd:
                bestd = d
                target = (cx, cy)
        best_key = None
        best_move = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # Higher is better: increase distance to opponent and to chosen corner progression.
            key = (man(nx, ny, ox, oy), man(nx, ny, target[0], target[1]), -abs(nx - target[0]) - abs(ny - target[1]), -(dx * dx + dy * dy))
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])] if best_key is not None else [0, 0]

    # Pursue
    # Prefer minimizing distance to opponent; tie-break: move that also reduces distance to opponent's nearest corner.
    opp_nearest_corner = corners[0]
    bestc = man(corners[0][0], corners[0][1], ox, oy)
    for cx, cy in corners[1:]:
        d = man(cx, cy, ox, oy)
        if d < bestc:
            bestc = d
            opp_nearest_corner = (cx, cy)

    best_key = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        key = (-man(nx, ny, ox, oy), -man(nx, ny, opp_nearest_corner[0], opp_nearest_corner[1]), -abs(nx - ox) - abs(ny - oy), -(dx * dx + dy * dy))
        # key is negative distances so "max" is "min distance"
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])] if best_key is not None else [0, 0]