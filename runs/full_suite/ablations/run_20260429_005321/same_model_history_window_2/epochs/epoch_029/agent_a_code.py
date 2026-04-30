def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        tx, ty = ox, oy
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            # keep away from opponent and prefer moves that stay within bounds
            cand = (-d, nx, ny)
            if cand < (best[0], best[1], best[2]):
                best = (cand[0], cand[1], cand[2])
        dx, dy = best[1] - sx, best[2] - sy
        return [dx, dy]

    alpha = 0.6
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # one-step lookahead: pick move that makes our closest "contested" target best
        cur_best = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # smaller is better: we want targets we can reach sooner than opponent
            score = myd - alpha * opd
            if cur_best is None or score < cur_best or (score == cur_best and (rx, ry) < cur_res):
                cur_best = score
                cur_res = (rx, ry)
        # tie-break deterministically: prefer smaller my distance to chosen resource, then lexicographic move
        if cur_best is None:
            continue
        chosen_rx, chosen_ry = cur_res
        tieb = (cheb(nx, ny, chosen_rx, chosen_ry), dx, dy)
        val = (cur_best, tieb)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]