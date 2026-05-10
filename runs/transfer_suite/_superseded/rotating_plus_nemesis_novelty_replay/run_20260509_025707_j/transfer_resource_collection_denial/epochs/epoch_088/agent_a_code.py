def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    tr = observation.get("turns_remaining", 0)
    # Opponent greedy one-step prediction toward closest resource (ties by distance then x,y).
    def opp_next(px, py):
        best = None
        for r in resources:
            rx, ry = r[0], r[1]
            d = dist(px, py, rx, ry)
            key = (d, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        rx, ry = best[1], best[2]
        bestd = None
        bestm = (0, 0)
        for dx, dy in dirs:
            nx, ny = px + dx, py + dy
            if not ok(nx, ny):
                continue
            nd = dist(nx, ny, rx, ry)
            if bestd is None or nd < bestd or (nd == bestd and (dx, dy) < bestm):
                bestd = nd
                bestm = (dx, dy)
        return bestm

    odx, ody = opp_next(ox, oy)
    nox, noy = ox + odx, oy + ody

    # Choose move that maximizes our advantage over the predicted opponent across contested resources.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        val = 0
        for r in resources:
            rx, ry = r[0], r[1]
            myd = dist(nx, ny, rx, ry)
            oppd = dist(nox, noy, rx, ry)
            # Base contest: strongly prefer where we can be closer than opponent.
            contest = (oppd - myd)
            # Row-sweep defense: if opponent can sweep that row quickly, we bias toward breaking contest earlier.
            row_pressure = 0
            if ry == noy:
                row_pressure = 2
            # Prefer closer targets to reduce time-to-collection; also prefer earlier in game.
            time_bias = 0.9 if tr > 6 else 1.2
            val += (contest * 3 - myd * time_bias + row_pressure * (myd - oppd))
        # Small deterministic tie-break: prefer moving toward center to reduce getting stuck.
        center_bias = -((abs((nx - (w - 1) / 2)) + abs((ny - (h - 1) / 2))) * 0.05)
        val += center_bias
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]