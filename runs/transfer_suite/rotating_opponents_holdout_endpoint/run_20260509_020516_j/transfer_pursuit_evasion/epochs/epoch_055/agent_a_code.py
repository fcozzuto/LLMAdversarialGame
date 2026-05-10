def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def sqdist(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        if not valid(nsx, nsy):
            nsx, nsy = sx, sy
        # Opponent best-response: maximize our distance (evasion)
        max_d = None
        for odx, ody in moves:
            nox, noy = ox + odx, oy + ody
            if not valid(nox, noy):
                nox, noy = ox, oy
            d = sqdist(nsx, nsy, nox, noy)
            if max_d is None or d > max_d:
                max_d = d
        # Minimize the opponent's best response distance; tie-break by also approaching corner farther from opponent
        corner_targets = [(0, h - 1), (w - 1, 0), (0, 0), (w - 1, h - 1)]
        t = corner_targets[0]
        if corner_targets:
            # choose target that is farther from opponent to encourage cutting off edges
            t = max(corner_targets, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        tie = sqdist(nsx, nsy, t[0], t[1])
        val = (max_d, tie)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]