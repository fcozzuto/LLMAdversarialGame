def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    try:
        w = int(w)
    except:
        w = 8
    try:
        h = int(h)
    except:
        h = 8
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    targets = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                targets.append((x, y))
    if not targets:
        for p in observation.get("resources") or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y):
                    targets.append((x, y))

    if targets:
        cx, cy = ox, oy
        # Prefer cells that are closer to us; tie-break to reduce distance to opponent's cell (more likely contested).
        targets.sort(key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), abs(t[0] - cx) + abs(t[1] - cy), t[0], t[1]))
        tx, ty = targets[0]
    else:
        tx, ty = w // 2, h // 2

    best = (None, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Score: maximize closeness to target, avoid getting closer to opponent only when no target.
        dist = abs(nx - tx) + abs(ny - ty)
        opp_dist = abs(nx - ox) + abs(ny - oy)
        score = -dist * 10 + (opp_dist if not targets else 0) + (0 if dx == 0 and dy == 0 else 1)
        if score > best[1] or (score == best[1] and (dx, dy) < best[0]):
            best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    dx, dy = best[0]
    return [int(dx), int(dy)]