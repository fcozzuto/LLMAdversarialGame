def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_pursuer(role):
        r = (role or "").lower()
        return ("pursuer" in r) or ("chaser" in r) or ("pursuit" in r) or ("hunter" in r)

    self_pursuer = is_pursuer(observation.get("self_role"))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # Deterministic tie-break: prefer moves that keep us closer to the "best corner" for our objective.
    best_corner_for = None
    if self_pursuer:
        # If we can choose, head to the corner that is closest to the opponent (tightening geometry).
        best_corner_for = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    else:
        # Evader: head to the corner farthest from the opponent.
        best_corner_for = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        d_opp = dist2(nx, ny, ox, oy)
        d_corner = dist2(nx, ny, best_corner_for[0], best_corner_for[1])

        # Pursuer: maximize closeness to opponent (minimize d_opp), with secondary preference for corner pressure.
        # Evader: maximize distance from opponent (maximize d_opp), with secondary preference for running to corner.
        val = (-d_opp if self_pursuer else d_opp, -d_corner if self_pursuer else d_corner)

        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]