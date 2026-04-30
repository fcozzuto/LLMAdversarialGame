def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(x1, y1, x2, y2):
        d = abs(x1 - x2) + abs(y1 - y2)
        return d

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def best_value(ax, ay):
        if not resources:
            return 0
        best = -10**18
        for tx, ty in resources:
            ds = md(ax, ay, tx, ty)
            do = md(ox, oy, tx, ty)
            if ds <= do:
                v = 10000 - ds * 10 - (do - ds)
            else:
                v = 50 - (ds - do) * 30 - do
            if ds == 0:
                v += 10**6
            best = v if v > best else best
        return best

    # Two-step greedy lookahead (ours only), deterministic.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v1 = best_value(nx, ny)
        # Next-step lookahead: pick our best move from (nx, ny) deterministically by score.
        v2 = -10**18
        for ddx, ddy in deltas:
            nnx, nny = nx + ddx, ny + ddy
            if not valid(nnx, nny):
                continue
            v2c = best_value(nnx, nny) - 0.1 * (abs(ddx) + abs(ddy))
            if v2c > v2:
                v2 = v2c
        score = v2 + v1 * 0.3
        # Tie-break: move that reduces distance to the single best resource now.
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]