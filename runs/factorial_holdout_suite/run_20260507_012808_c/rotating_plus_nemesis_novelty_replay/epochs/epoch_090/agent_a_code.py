def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    def step_options():
        return [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]

    tx, ty = w // 2, h // 2
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            myd = manh(sx, sy, rx, ry)
            opd = manh(ox, oy, rx, ry)
            # Prefer resources where we're not behind; deterministic tie-break by position
            key = (opd - myd, -myd, -rx, -ry)
            if best is None or key > best_key:
                best = (rx, ry)
                best_key = key
        tx, ty = best

    best_move = None
    best_val = None
    for dx, dy in step_options():
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_target = manh(nx, ny, tx, ty)
        d_from_opp = manh(nx, ny, ox, oy)
        # Primary: minimize distance to target; secondary: maximize distance from opponent; tertiary: deterministic order
        val = (-d_to_target, d_from_opp, -dx, -dy)
        if best_move is None or val > best_val:
            best_move = (dx, dy)
            best_val = val

    if best_move is None:
        # Last resort: try to stay
        if 0 <= sx < w and 0 <= sy < h and (sx, sy) not in obstacles:
            return [0, 0]
        # Otherwise pick any in-bounds non-obstacle neighbor deterministically
        for dx, dy in step_options():
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    return [int(best_move[0]), int(best_move[1])]