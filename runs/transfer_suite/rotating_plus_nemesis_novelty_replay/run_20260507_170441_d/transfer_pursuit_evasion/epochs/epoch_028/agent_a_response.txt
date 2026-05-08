def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def sqdist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    best = None
    best_val = None
    for dx, dy, nsx, nsy in candidates:
        opp_best = None
        opp_best_val = None
        # Opponent evades: choose move that maximizes distance from our new position.
        for odx, ody in dirs:
            nox, noy = ox + odx, oy + ody
            if not ok(nox, noy):
                continue
            val = sqdist(nsx, nsy, nox, noy)
            if opp_best_val is None or val > opp_best_val:
                opp_best_val = val
                opp_best = (odx, ody, nox, noy)
        # If opponent has no legal moves, just evaluate current.
        if opp_best is None:
            final_d2 = sqdist(nsx, nsy, ox, oy)
        else:
            final_d2 = sqdist(nsx, nsy, opp_best[2], opp_best[3])

        # Minimize the evader's best-response distance; tie-break deterministically by closeness now.
        tie = sqdist(sx, sy, ox, oy)
        score = (-final_d2, tie)
        if best_val is None or score < best_val:
            best_val = score
            best = (dx, dy)

    return [best[0], best[1]]