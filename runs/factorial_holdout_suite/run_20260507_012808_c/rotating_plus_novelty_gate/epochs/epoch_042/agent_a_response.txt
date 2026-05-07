def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = 0 if sx < 0 else (w - 1 if sx >= w else int(sx))
    sy = 0 if sy < 0 else (h - 1 if sy >= h else int(sy))
    ox = 0 if ox < 0 else (w - 1 if ox >= w else int(ox))
    oy = 0 if oy < 0 else (h - 1 if oy >= h else int(oy))

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in (observation.get("resources") or []):
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        target = (w - 1 - sx, h - 1 - sy)  # deterministic fallback
        tx, ty = target
    else:
        best = None
        best_key = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            margin = opd - myd  # prefer places opponent is farther from
            key = (margin, -myd, -(rx * 31 + ry * 17))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        # prefer minimal distance, then minimal squared distance to target, then deterministic preference
        sd = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        pref = (dx + 1) * 10 + (dy + 1)
        score = (-d, -sd, -pref)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]