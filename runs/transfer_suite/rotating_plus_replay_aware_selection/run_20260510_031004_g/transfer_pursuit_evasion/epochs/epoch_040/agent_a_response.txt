def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("hunter" in self_role) or (self_role == "pursuer")
    if not pursuer and opponent_role:
        pursuer = not ("evad" in opponent_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Deterministic target: corner opposite/diagonal bias.
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if pursuer:
        tx, ty = ox, oy
    else:
        # Farthest corner from pursuer/opponent, with slight bias away from opponent.
        bestc = None
        bestv = -1
        for cx, cy in corners:
            v = d2(cx, cy, ox, oy)
            if bestc is None or v > bestv:
                bestc = (cx, cy)
                bestv = v
        tx, ty = bestc

    best_move = [0, 0]
    if pursuer:
        best_score = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # Prefer reducing distance to opponent; slight penalty for closeness to obstacles.
            score = -d2(nx, ny, ox, oy)
            if obs:
                mind = 10**9
                for (px, py) in obs:
                    mind = min(mind, d2(nx, ny, px, py))
                score += 0.01 * mind
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
    else:
        best_score = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # Prefer maximizing distance from opponent while moving toward target corner.
            score = d2(nx, ny, ox, oy) - 0.01 * d2(nx, ny, tx, ty)
            if obs:
                mind = 10**9
                for (px, py) in obs:
                    mind = min(mind, d2(nx, ny, px, py))
                score += 0.02 * mind
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    nx, ny = sx + best_move[0], sy + best_move[1]
    if ok(nx, ny):
        return best_move
    return [0, 0]