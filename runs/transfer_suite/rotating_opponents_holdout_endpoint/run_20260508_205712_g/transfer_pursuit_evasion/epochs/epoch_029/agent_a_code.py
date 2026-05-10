def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obstacles.add((int(a[0]), int(a[1])))

    role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("pursuer" in role) or (role == "" and ("pursuer" in opp_role) and ("evader" not in role))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Deterministic tie-breaking: prefer earlier move in list; then prefer smaller distance to center (for pursuer),
    # or larger distance to center (for evader).
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_dx, best_dy = 0, 0
    if is_pursuer:
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            cc = abs(nx - cx) + abs(ny - cy)
            key = (-d, -cc)  # maximize: distance decrease, and go toward center by preferring smaller cc via -cc
            if best_key is None or key > best_key:
                best_key = key
                best_dx, best_dy = dx, dy
    else:
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            cc = abs(nx - cx) + abs(ny - cy)
            key = (d, cc)  # maximize: distance, and go away from center by preferring larger cc
            if best_key is None or key > best_key:
                best_key = key
                best_dx, best_dy = dx, dy

    if valid(sx + best_dx, sy + best_dy):
        return [int(best_dx), int(best_dy)]
    return [0, 0]