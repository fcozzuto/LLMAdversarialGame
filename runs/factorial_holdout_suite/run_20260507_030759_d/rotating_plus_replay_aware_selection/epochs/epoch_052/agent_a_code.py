def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    if w <= 0 or h <= 0:
        return [0, 0]
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    best = None
    best_key = (10**9, 10**9)

    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue

        # Prefer collecting soon, especially resources we beat the opponent to.
        cur_best = (10**9, 10**9)  # (score, our_time)
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            our_t = cheb(nsx, nsy, rx, ry)
            if our_t == 0:
                our_t = 0
            opp_t = cheb(ox, oy, rx, ry)
            # Heuristic: strongly penalize being slower; lightly encourage shorter times.
            lead = our_t - opp_t
            penalty = 0
            if lead > 0:
                penalty = 3 * lead + (lead * lead)
            # Small preference for moves that also reduce absolute time.
            score = penalty * 100 + our_t
            key = (score, our_t)
            if key < cur_best:
                cur_best = key

        # Deterministic tie-break: choose smaller mdx/ then mdy via tuple.
        key2 = (cur_best[0], cur_best[1], mdx, mdy)
        if best is None or key2 < best_key:
            best = [mdx, mdy]
            best_key = key2

    return best if best is not None else [0, 0]