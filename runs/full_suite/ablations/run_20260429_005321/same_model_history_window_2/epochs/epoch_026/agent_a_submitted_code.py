def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def best_score(tx, ty, rx, ry):
        d = abs(tx - rx) + abs(ty - ry)
        if d == 0:
            d = 0
        return d

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cx, cy = w // 2, h // 2
    targets = resources if resources else [(cx, cy)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        rmin = min(best_score(nx, ny, rx, ry) for rx, ry in targets)
        omin = min(best_score(nx, ny, rx, ry) for rx, ry in [(ox, oy)])
        # Prefer reducing distance to resources; add small penalty if moving toward opponent.
        score = (rmin * 1000) + (omini * 10)
        if best is None or score < best[0]:
            best = (score, [dx, dy])

    if best is not None:
        return best[1]

    # Fallback: stay put if possible, else any valid move.
    if valid(sx, sy):
        return [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
    return [0, 0]