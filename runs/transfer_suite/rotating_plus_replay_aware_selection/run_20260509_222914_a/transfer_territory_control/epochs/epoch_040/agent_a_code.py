def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def parse_pos(v):
        try:
            if isinstance(v, (list, tuple)) and len(v) >= 2:
                return int(v[0]), int(v[1])
        except Exception:
            pass
        return 0, 0

    sx, sy = parse_pos(observation.get("self_position"))
    ox, oy = parse_pos(observation.get("opponent_position"))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                obs.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y) and (x, y) not in obs:
                unclaimed.append((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    best = (10**18, 0, 0)
    targets = unclaimed if unclaimed else [(w // 2, h // 2), (ox, oy)]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        score = 0
        if targets:
            tx, ty = min(targets, key=lambda t: (abs(t[0] - nx) + abs(t[1] - ny), t[0], t[1]))
            score = abs(tx - nx) + abs(ty - ny)
        d_from_opp = abs(ox - nx) + abs(oy - ny)
        score -= min(8, d_from_opp)
        cand = (score, -d_from_opp, dx, dy)
        if cand < best:
            best = cand

    return [int(best[2]), int(best[3])]