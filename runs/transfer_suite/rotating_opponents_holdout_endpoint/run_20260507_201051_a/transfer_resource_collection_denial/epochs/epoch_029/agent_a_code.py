def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def norm_pos(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            return (x, y) if 0 <= x < w and 0 <= y < h else None
        if isinstance(p, dict):
            pos = p.get("position", p.get("pos", p.get("location", p.get("cell", None))))
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                x, y = int(pos[0]), int(pos[1])
                return (x, y) if 0 <= x < w and 0 <= y < h else None
        return None

    s = norm_pos(observation.get("self_position", (0, 0))) or (0, 0)
    o = norm_pos(observation.get("opponent_position", (0, 0))) or (0, 0)
    sx, sy = s
    ox, oy = o

    obs = set()
    for p in (observation.get("obstacles") or []):
        c = norm_pos(p)
        if c is not None:
            obs.add(c)

    targets = []
    for p in (observation.get("resources") or []):
        c = norm_pos(p)
        if c is not None and c not in obs:
            targets.append(c)
    if not targets:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets.sort(key=lambda c: (dist(s, c), c[0], c[1]))
    tx, ty = targets[0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d_to = abs(nx - tx) + abs(ny - ty)
        d_opp = abs(nx - ox) + abs(ny - oy)
        score = (d_to, -d_opp, abs(dx) + abs(dy), dx, dy)
        if best is None or score < best_score:
            best = (dx, dy)
            best_score = score
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]