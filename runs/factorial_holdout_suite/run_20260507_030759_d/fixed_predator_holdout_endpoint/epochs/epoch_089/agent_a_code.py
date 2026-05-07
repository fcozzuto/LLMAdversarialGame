def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        t = a - c
        t = -t if t < 0 else t
        u = b - d
        u = -u if u < 0 else u
        return t + u

    # Primary: pick a resource we can reach no later than opponent (deny-first).
    # Fallback: if none, pick resource where we minimize opponent advantage (most contestable).
    best = None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        can_take = 1 if sd <= od else 0
        # Deterministic ordering tie-break: favor higher advantage, then smaller self distance, then lexicographic.
        key = (can_take, od - sd, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Try preferred move; if blocked by obstacle, try axis moves that still reduce distance; else stay.
    candidates = [(dx, dy)]
    for ax, ay in [(dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]:
        if (ax, ay) not in candidates:
            candidates.append((ax, ay))

    def dist_after(ddx, ddy):
        nx, ny = sx + ddx, sy + ddy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            return 10**9
        return md(nx, ny, tx, ty)

    best_step = (0, 0)
    best_step_val = 10**9
    for ddx, ddy in candidates:
        v = dist_after(ddx, ddy)
        if v < best_step_val or (v == best_step_val and (ddx, ddy) == candidates[0]):
            best_step_val = v
            best_step = (ddx, ddy)
    return [int(best_step[0]), int(best_step[1])]