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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    prefer = [m for m in moves if m != (0, 0)]
    cand = prefer if any(ok(sx + dx, sy + dy) for dx, dy in prefer) else moves

    if pursuer:
        best = None
        bestv = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = dist2(nx, ny, ox, oy)
            if bestv is None or v < bestv:
                bestv, best = v, [dx, dy]
        return best if best is not None else [0, 0]
    else:
        best = None
        bestv = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = dist2(nx, ny, ox, oy)
            if bestv is None or v > bestv:
                bestv, best = v, [dx, dy]
        return best if best is not None else [0, 0]