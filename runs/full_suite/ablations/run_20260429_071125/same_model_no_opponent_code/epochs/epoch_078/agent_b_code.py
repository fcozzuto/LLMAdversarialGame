def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Prefer targets we reach no later than opponent; tie-break toward safer/higher progress.
        win_margin = do - ds
        score = (win_margin, -ds, -ry, -rx)
        if best is None or score > best[0]:
            best = (score, rx, ry)
    _, tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_new = dist(nx, ny, tx, ty)
        # Also mildly avoid moving into squares very close to opponent (deterministic risk aversion).
        d_opp = dist(nx, ny, ox, oy)
        risk = 0 if d_opp >= 3 else (3 - d_opp)
        score = (-d_new, -risk, -ny, -nx, -abs(dx) - abs(dy))
        if bestm is None or score > bestm[0]:
            bestm = (score, dx, dy)
    if bestm is None:
        return [0, 0]
    return [int(bestm[1]), int(bestm[2])]