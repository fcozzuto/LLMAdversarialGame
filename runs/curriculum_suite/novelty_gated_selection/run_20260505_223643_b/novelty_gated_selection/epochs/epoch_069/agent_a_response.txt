def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    res_sorted = sorted(resources, key=lambda r: dist2(ox, oy, r[0], r[1]))
    best_r = res_sorted[0]
    # If opponent is extremely close to their likely target, try to interfere with the next one.
    if dist2(ox, oy, best_r[0], best_r[1]) <= 2 and len(res_sorted) > 1:
        target = res_sorted[1]
    else:
        target = best_r

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_val = -10**30
    best_move = [0, 0]
    tx, ty = target

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myd = dist2(nx, ny, tx, ty)
        opd = dist2(ox, oy, tx, ty)
        # Prefer: reduce my distance to target while increasing opponent's advantage.
        # Tie-break: closer to target, then closer to another good resource deterministically.
        val = (opd - myd) * 1000 - myd
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move