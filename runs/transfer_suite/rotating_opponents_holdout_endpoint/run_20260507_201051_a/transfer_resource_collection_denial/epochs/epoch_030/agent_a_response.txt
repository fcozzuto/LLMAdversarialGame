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

    s = norm_pos(observation.get("self_position")) or (0, 0)
    o = norm_pos(observation.get("opponent_position")) or (0, 0)
    sx, sy = s
    ox, oy = o

    obstacles = set()
    for p in observation.get("obstacles") or []:
        c = norm_pos(p)
        if c is not None:
            obstacles.add(c)

    resources = []
    for p in observation.get("resources") or []:
        c = norm_pos(p)
        if c is not None and c not in obstacles:
            resources.append(c)
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Race-aware target: prioritize resources where we're closer (or at least not much behind).
    best = None
    best_key = None
    for r in resources:
        ds = dist(s, r)
        do = dist(o, r)
        # Lower is better: want small ds; penalize if opponent is significantly closer.
        key = (ds, max(0, do - ds), r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best = r
    tx, ty = best

    desired = (0, 0)
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    desired = (dx, dy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Prefer desired move, then moves that reduce distance to target.
    candidates = []
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        candidates.append((0 if (mx, my) == desired else 1, dist((nx, ny), (tx, ty)), mx, my))
    candidates.sort()
    mx, my = candidates[0][2], candidates[0][3]
    return [int(mx), int(my)]