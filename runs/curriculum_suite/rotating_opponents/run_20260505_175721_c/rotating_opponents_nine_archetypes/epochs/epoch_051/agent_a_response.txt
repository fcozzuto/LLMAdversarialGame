def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def md(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # deterministic safe drift toward center
        tx, ty = (w - 1) // 2, (h - 1) // 2
        candidates = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((md(nx, ny, tx, ty), dx, dy))
        candidates.sort()
        return [candidates[0][1], candidates[0][2]] if candidates else [0, 0]

    # Contested resource selection: prefer resources we can reach earlier than opponent.
    best = None
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # primary: advantage (opponent farther), then our distance, then deterministic cell ordering
        key = (do - ds, -ds, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))

    (tx, ty) = best[1]

    # primary greedy step toward target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
        return [dx, dy]

    # fallback: choose best valid move minimizing distance to target; deterministic tie-break.
    bestm = None
    for ddx, ddy in moves:
        px, py = sx + ddx, sy + ddy
        if not (0 <= px < w and 0 <= py < h): 
            continue
        if (px, py) in obstacles:
            continue
        score = (md(px, py, tx, ty), md(px, py, ox, oy), ddx, ddy)
        if bestm is None or score < bestm[0]:
            bestm = (score, ddx, ddy)
    return [bestm[1], bestm[2]] if bestm else [0, 0]