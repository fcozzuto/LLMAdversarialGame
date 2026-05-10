def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) or ("evad" not in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def min_obs_d(nx, ny):
        best = 10**9
        for (ex, ey) in obs:
            d = abs(nx - ex) + abs(ny - ey)
            if d < best:
                best = d
        return 0 if best == 10**9 else best

    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    if pursuer:
        best_score = None
        best_move = None
        for dx, dy, nx, ny in cand:
            v = dist2(nx, ny, ox, oy)
            dO = min_obs_d(nx, ny)
            score = (-v, dO, abs(nx - ox) + abs(ny - oy))
            if best_score is None or score > best_score:
                best_score, best_move = score, [dx, dy]
        return best_move

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    best_score = None
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = dist2(nx, ny, ox, oy)
        md = abs(nx - tx) + abs(ny - ty)
        dO = min_obs_d(nx, ny)
        score = (v, -md, dO, -abs(dx) - abs(dy))
        if best_score is None or score > best_score:
            best_score, best_move = score, [dx, dy]
    if best_move is None:
        return [0, 0]
    return best_move