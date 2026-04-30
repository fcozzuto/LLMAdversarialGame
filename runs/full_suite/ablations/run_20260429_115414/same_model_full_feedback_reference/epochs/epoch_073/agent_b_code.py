def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                res.append((x, y))

    if not res:
        dx = -1 if sx > ox else (1 if sx < ox else 0)
        dy = -1 if sy > oy else (1 if sy < oy else 0)
        return [dx, dy]

    best = res[0]
    best_score = -10**9
    for x, y in res:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        score = (do - ds) * 10 - ds
        if score > best_score:
            best_score = score
            best = (x, y)

    tx, ty = best
    dx = 0 if sx == tx else (1 if tx > sx else -1)
    dy = 0 if sy == ty else (1 if ty > sy else -1)

    cand = []
    for mx, my in ((dx, dy), (dx, 0), (0, dy), (0, 0)):
        nx, ny = sx + mx, sy + my
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
            cand.append((mx, my))
    if not cand:
        for mx, my in ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)):
            nx, ny = sx + mx, sy + my
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
                cand.append((mx, my))
                break
    mx, my = cand[0] if cand else (0, 0)
    return [mx, my]