def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def step_towards(tx, ty):
        dx = tx - sx
        dy = ty - sy
        mx = 0 if dx == 0 else (1 if dx > 0 else -1)
        my = 0 if dy == 0 else (1 if dy > 0 else -1)
        nx, ny = sx + mx, sy + my
        if (nx, ny) in obstacles:
            # Try axis-aligned alternative deterministically
            if (sx + mx, sy) not in obstacles:
                return [mx, 0]
            if (sx, sy + my) not in obstacles:
                return [0, my]
            if (sx + mx, sy) in obstacles and (sx, sy + my) in obstacles:
                return [0, 0]
        return [mx, my]

    if resources:
        best = None
        best_key = None
        # Prefer resources we can reach first; if tie, closer to us; then prefer being farther from opponent.
        for rx, ry in resources:
            sd = manh(sx, sy, rx, ry)
            od = manh(ox, oy, rx, ry)
            slack = od - sd  # positive means we are closer (or opponent farther)
            key = (slack, -sd, -rx, -ry, sd)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
        return step_towards(tx, ty)

    # No visible resources: move toward opponent's side to intercept center-ish; deterministic fallback.
    tx, ty = (w - 1, h - 1) if (sx + sy) % 2 == 0 else (0, h - 1)
    return step_towards(tx, ty)