def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def pos(p, default):
        try:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
            elif isinstance(p, dict):
                x = p.get("x", p.get("X", p.get("col", p.get("cx", default[0]))))
                y = p.get("y", p.get("Y", p.get("row", p.get("cy", default[1]))))
                x, y = int(x), int(y)
            else:
                return default
            if 0 <= x < w and 0 <= y < h:
                return (x, y)
        except Exception:
            pass
        return default

    sp = pos(observation.get("self_position", None), (0, 0))
    op = pos(observation.get("opponent_position", None), (w - 1, h - 1))
    sx, sy = sp
    ox, oy = op

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        p = pos(o, None)
        if p is not None:
            obstacles.add(p)

    resources = []
    for r in (observation.get("resources", []) or []):
        p = pos(r, None)
        if p is not None and p not in obstacles:
            resources.append(p)

    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        if dx != 0:
            cand = (dx, 0)
        else:
            cand = (0, dy)
        nx, ny = sx + cand[0], sy + cand[1]
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [cand[0], cand[1]]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target = min(resources, key=lambda p: dist((sx, sy), p))
    tx, ty = target
    best = None
    best_score = -10**9

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        curd = abs(sx - tx) + abs(sy - ty)
        newd = abs(nx - tx) + abs(ny - ty)
        score = (curd - newd) * 1000 - dist((nx, ny), (ox, oy))
        if dx == 0 and dy == 0:
            score -= 5
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    return [best[0], best[1]]