def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            ax, ay = int(p[0]), int(p[1])
        except Exception:
            continue
        if 0 <= ax < w and 0 <= ay < h:
            obs.add((ax, ay))

    role = (observation.get("self_role", "") or "").lower()
    evade = ("evad" in role) and ("purs" not in role)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best = None
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            ddx, ddy = nx - ox, ny - oy
            d2 = ddx * ddx + ddy * ddy
            val = d2 if evade else -d2
            if best is None or val > best_val or (val == best_val and (dx, dy) < best):
                best = (dx, dy)
                best_val = val

    if best is not None:
        return [int(best[0]), int(best[1])]
    if ok(sx, sy):
        return [0, 0]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
    return [0, 0]