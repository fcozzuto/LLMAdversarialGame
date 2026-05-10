def choose_move(observation):
    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            if "position" in v:
                p = v["position"]
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    return int(p[0]), int(p[1])
            if "x" in v and "y" in v:
                return int(v["x"]), int(v["y"])
        return 0, 0

    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = to_xy(observation.get("self_position", (0, 0)))
    ox, oy = to_xy(observation.get("opponent_position", (0, 0)))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        x, y = to_xy(p if not isinstance(p, dict) else p)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        x, y = to_xy(r)
        if 0 <= x < w and 0 <= y < h:
            resources.append((x, y))

    def dist(a, b, c, d):
        ax = a - c
        ay = b - d
        ax = -ax if ax < 0 else ax
        ay = -ay if ay < 0 else ay
        return ax if ax > ay else ay

    best = None
    best_score = -10**18
    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    target = resources[0] if resources else (ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        score = 0
        if resources:
            dmin = 10**9
            for rx, ry in resources:
                dmin = min(dmin, dist(nx, ny, rx, ry))
            score += 1000 - dmin
        else:
            score += 500 - dist(nx, ny, ox, oy)
        score -= 2 * dist(nx, ny, ox, oy)
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return best