def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def step_toward(px, py, tx, ty):
        dx = 0 if tx == px else (1 if tx > px else -1)
        dy = 0 if ty == py else (1 if ty > py else -1)
        return [dx, dy]

    # Pick resource where we are closer than opponent (chebyshev distance).
    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Higher is better: we want od-sd large, then smaller our distance, then deterministic position.
        key = (od - sd, -sd, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Evaluate candidate moves: prefer ones that reduce our distance to target;
    # avoid stepping onto obstacles; deterministic tie-break.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = sx + dx
            ny = sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            ourd = cheb(nx, ny, tx, ty)
            oppd = cheb(ox, oy, tx, ty)
            # Encourage progress and slight "deny" if we keep ourselves well ahead.
            key = (-ourd, (oppd - ourd), -nx, -ny)
            candidates.append((key, [dx, dy]))
    candidates.sort(reverse=True, key=lambda x: x[0])
    return candidates[0][1] if candidates else [0, 0]