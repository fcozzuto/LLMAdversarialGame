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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not inb(sx, sy):
        for dx, dy in moves:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if not res:
        # fallback: move toward opponent (slight lex tie-break)
        best = [10**9, 10**9, 10**9, 0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = max(abs(nx - ox), abs(ny - oy))
            cand = [d, abs(nx - ox) + abs(ny - oy), (dx + 2) * 4 + (dy + 2), dx, dy]
            if cand < best:
                best = cand
        return [best[3], best[4]]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    best = [10**9, 10**9, 10**9, 0, 0, 0]  # [my-better, mydist, lex, dx, dy, target_index]
    for ti, t in enumerate(res):
        myd = dist((sx, sy), t)
        opd = dist((ox, oy), t)
        my_better = myd - opd  # negative means I'm closer
        # prioritize: (1) I'm closer; (2) closer absolute; (3) deterministic target ordering
        if (my_better, myd, ti) < (best[0], best[1], best[5]):
            best = [my_better, myd, 0, 0, 0, ti]

    # choose move that improves toward the chosen target while keeping obstacle legality
    target = res[best[5]]
    bestm = [10**9, 10**9, 10**9, 0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = dist((nx, ny), target)
        # also consider not allowing opponent to be closer on next step
        opp_next = dist((ox, oy), target)
        # lex tie-break using dx,dy ordering
        cand = [nd, (nd - opp_next), (dx + 1) * 3 + (dy + 1), dx, dy]
        if cand < bestm:
            bestm = cand
    return [bestm[3], bestm[4]]