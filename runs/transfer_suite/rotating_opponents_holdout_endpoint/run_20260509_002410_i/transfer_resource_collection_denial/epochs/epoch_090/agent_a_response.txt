def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        ax = ax - bx
        ay = ay - by
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax + ay

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    moves.append((0, 0, sx, sy))  # staying still allowed

    best = None
    for dx, dy, nx, ny in moves:
        score = -10**9
        for rx, ry in resources:
            if (nx, ny) == (rx, ry):
                s = 10**6 + 1000  # strongly prioritize immediate pickup
            else:
                d_self = md(nx, ny, rx, ry)
                d_opp = md(ox, oy, rx, ry)
                s = (d_opp - d_self) * 100 - d_self  # maximize being closer than opponent
            if s > score:
                score = s
        cand = (score, dx, dy)
        if best is None or cand > best:
            best = cand

    return [int(best[1]), int(best[2])]