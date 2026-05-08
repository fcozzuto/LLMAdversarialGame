def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def norm_pos(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            return (x, y) if 0 <= x < w and 0 <= y < h else None
        return None

    s = norm_pos(observation.get("self_position")) or (0, 0)
    o = norm_pos(observation.get("opponent_position")) or (w - 1, h - 1)
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

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    def clamp_step(d):
        return -1 if d < 0 else (1 if d > 0 else 0)

    def move_candidates(cur, target):
        cx, cy = cur
        tx, ty = target
        base_dx = clamp_step(tx - cx)
        base_dy = clamp_step(ty - cy)
        moves = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    pass
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    dist2 = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
                    moves.append((dist2, abs(dx) + abs(dy), dx, dy))
        moves.sort()
        return [(m[2], m[3]) for m in moves]

    best = None
    best_key = None
    for r in resources:
        our = cheb(s, r)
        opp = cheb(o, r)
        # Prefer closer resources; break ties by denying (larger opp distance is worse).
        key = (round(our, 6), -round(opp, 6), r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best = r

    tx, ty = best
    candidates = move_candidates(s, best)
    if not candidates:
        return [0, 0]
    dx, dy = candidates[0]
    return [int(dx), int(dy)]