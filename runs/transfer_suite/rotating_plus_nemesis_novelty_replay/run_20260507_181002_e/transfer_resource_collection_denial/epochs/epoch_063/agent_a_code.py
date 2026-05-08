def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def get_xy(v, fallback=None):
        if fallback is None:
            fallback = (0, 0)
        try:
            if isinstance(v, (list, tuple)) and len(v) >= 2:
                return (int(v[0]), int(v[1]))
            if isinstance(v, dict):
                p = v.get("position", v.get("pos", v.get("location", None)))
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    return (int(p[0]), int(p[1]))
        except Exception:
            pass
        return fallback

    sx, sy = get_xy(observation.get("self_position"), (0, 0))
    ox, oy = get_xy(observation.get("opponent_position"), (sx, sy))

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        ox2, oy2 = get_xy(o, None) if isinstance(o, dict) else (None, None)
        if ox2 is None:
            continue
        if 0 <= ox2 < w and 0 <= oy2 < h:
            obstacles.add((ox2, oy2))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        rx, ry = get_xy(r, None) if isinstance(r, dict) else (None, None)
        if rx is None:
            continue
        if free(rx, ry):
            resources.append((rx, ry))

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                candidates.append((dx, dy))

    if not candidates:
        return [0, 0]

    best = None
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if resources:
            # Prefer nearest resource; break ties by moving away from opponent.
            md = min(dist2(nx, ny, rx, ry) for rx, ry in resources)
            od = dist2(nx, ny, ox, oy)
            score = (0, -md, od)  # fewer steps to resource, then farther from opponent
        else:
            # No resources known: try to stay away from opponent.
            od = dist2(nx, ny, ox, oy)
            score = (1, od)
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]