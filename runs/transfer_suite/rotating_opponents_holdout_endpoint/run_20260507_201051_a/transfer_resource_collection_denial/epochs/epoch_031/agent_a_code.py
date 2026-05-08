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

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_row_pref = -abs(1 + sy - oy)  # prefer rows farther from opponent's sweep row (deterministic)
    best_r = resources[0]
    best_key = None
    for r in resources:
        sd = man(s, r)
        od = man(o, r)
        row_sep = -abs(r[1] - oy)  # higher when r is on different row than opponent
        # Race win pressure + row separation; also slightly favor closer targets.
        key = ((od - sd), (row_sep + opp_row_pref), (-sd), (-abs(r[0] - sx)))
        if best_key is None or key > best_key:
            best_key = key
            best_r = r

    tx, ty = best_r
    target = (tx, ty)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if (tx, ty) == s:
        return [0, 0]

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer moves that reduce distance to target and preserve race advantage.
        ns = (nx, ny)
        sd2 = man(ns, target)
        od2 = man(o, target)
        val = ((od2 - sd2), (-sd2), (-abs((nx - tx)) - abs((ny - ty))), (dx, dy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]