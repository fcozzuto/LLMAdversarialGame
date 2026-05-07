def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    for rx, ry in resources:
        dself = dist(sx, sy, rx, ry)
        dop = dist(ox, oy, rx, ry)
        cand = (dself - dop, dself, rx, ry)
        if best is None or cand < best[0]:
            best = (cand, rx, ry)

    tx, ty = best[1], best[2]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        hit_ob = (nx, ny) in obstacles
        nd = dist(nx, ny, tx, ty)
        # Prefer non-obstacle; then reduce distance to target; then align direction deterministically; then lexicographic move.
        score = (1 if hit_ob else 0, nd, abs(tx - nx) + abs(ty - ny) - abs(tx - sx) - abs(ty - sy), dx, dy)
        scored.append((score, dx, dy))

    if not scored:
        return [0, 0]
    scored.sort(key=lambda t: t[0])
    return [int(scored[0][1]), int(scored[0][2])]