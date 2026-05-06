def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_adv(px, py):
        best = None  # (adv, myd, oppd, tx, ty)
        for tx, ty in res:
            myd = cheb(px, py, tx, ty)
            oppd = cheb(ox, oy, tx, ty)
            adv = myd - oppd
            cand = (adv, myd, oppd, tx, ty)
            if best is None or cand < best:
                best = cand
        return best  # always exists

    cur_best = best_adv(sx, sy)

    best_move = None  # (score tuple, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        after_best = best_adv(nx, ny)
        # Prefer improving advantage; then shorter time; then higher reach to current best target; lex tie
        score = (after_best[0], after_best[1], -after_best[2], after_best[3], after_best[4])
        if best_move is None or score < best_move[0]:
            best_move = (score, dx, dy)

    if best_move is None:
        for dx, dy in moves:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]