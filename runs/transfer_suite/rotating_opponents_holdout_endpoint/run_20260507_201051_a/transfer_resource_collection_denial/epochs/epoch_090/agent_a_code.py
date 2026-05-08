def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy = (sp[0], sp[1]) if isinstance(sp, (list, tuple)) and len(sp) >= 2 else (0, 0)
    ox, oy = (op[0], op[1]) if isinstance(op, (list, tuple)) and len(op) >= 2 else (w - 1, h - 1)
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x = int(p[0]); y = int(p[1])
            except:
                continue
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x = int(p[0]); y = int(p[1])
            except:
                continue
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    if not res:
        return [0, 0]

    def dist(x, y, tx, ty):
        dx = x - tx
        if dx < 0: dx = -dx
        dy = y - ty
        if dy < 0: dy = -dy
        return dx + dy

    target = res[0]
    best = dist(sx, sy, target[0], target[1])
    for r in res[1:]:
        d = dist(sx, sy, r[0], r[1])
        if d < best:
            best = d
            target = r

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = 10**18
    tx, ty = target[0], target[1]
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist(nx, ny, tx, ty)
        # Small deterministic preference to avoid opponent overlap when possible
        opp = 0
        if abs(nx - ox) <= 0 and abs(ny - oy) <= 0:
            opp = 1
        score = d * 100 + opp
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]