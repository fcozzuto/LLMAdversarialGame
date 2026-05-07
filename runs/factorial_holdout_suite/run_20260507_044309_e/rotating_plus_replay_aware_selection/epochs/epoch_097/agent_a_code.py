def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def step_toward(tx, ty, x, y):
        # Prefer diagonal that reduces both; otherwise axis-first.
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        candidates = []
        if dx != 0 and dy != 0:
            candidates.append((dx, dy))
        candidates.append((dx, 0))
        candidates.append((0, dy))
        candidates.append((dx, dy))  # in case diagonal was blocked
        candidates.append((0, 0))
        for ddx, ddy in candidates:
            nx, ny = x + ddx, y + ddy
            if legal(nx, ny):
                return [ddx, ddy]
        return [0, 0]

    if not resources:
        # deterministic center fallback
        return step_toward(w // 2, h // 2, sx, sy)

    # Pick resource that we can reach earlier; if tie, pick one more central and less contested.
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        # Lower is better: prioritize smaller myd; but also prefer where we have advantage.
        key = (myd - 0.9 * (opd - myd), myd, -abs(rx - (w - 1) / 2) - abs(ry - (h - 1) / 2), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    return step_toward(tx, ty, sx, sy)