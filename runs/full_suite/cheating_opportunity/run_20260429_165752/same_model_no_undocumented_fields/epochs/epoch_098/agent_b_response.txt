def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not ok(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = (10**9, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if resources:
            score = 10**9
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                oppd = cheb(ox, oy, rx, ry)
                # Prefer grabbing/contesting resources; slight penalty for moving away from opponent
                local = (myd - oppd) * 6 + myd
                if local < score:
                    score = local
            # Encourage being closer to *some* resource and not too stationary
            score += 0 if (dx == 0 and dy == 0) else -0.5
        else:
            # No visible resources: move to reduce distance to opponent (block/crowd)
            score = cheb(nx, ny, ox, oy)
        # Deterministic tie-break: prefer smaller (dx,dy) in move list order
        if score < best[0]:
            best = (score, (dx, dy))

    dx, dy = best[1] if best[1] is not None else (0, 0)
    return [int(dx), int(dy)]