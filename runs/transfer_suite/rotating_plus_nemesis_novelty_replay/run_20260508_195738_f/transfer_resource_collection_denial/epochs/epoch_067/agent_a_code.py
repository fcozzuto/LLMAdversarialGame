def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Move toward the farthest-from-opponent corner to avoid getting stuck.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best_t = None
        best_v = -10**9
        for tx, ty in corners:
            v = cheb(tx, ty, ox, oy)
            if v > best_v:
                best_v = v
                best_t = (tx, ty)
        tx, ty = best_t
        best, bestm = -10**9, [0, 0]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty) + 0.02 * cheb(nx, ny, ox, oy)
            if v > best:
                best, bestm = v, [dx, dy]
        return bestm

    # Score a move by the best resource we can secure no later than opponent, plus small tie-breaks.
    best_overall, best_move = -10**18, [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Prefer to collect immediately, then win a contested resource quickly.
        best_res_score = -10**18
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Primary: maximize advantage; secondary: smaller self time; tertiary: larger opp time.
            adv = d_opp - d_self
            score = 1_000_000 * adv - 10_000 * d_self + d_opp
            if score > best_res_score:
                best_res_score = score
        # Additional safety: if we can't secure anything (all adv < 0), move to minimize our distance to nearest resource.
        if best_res_score < -10000:
            mind = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            fallback = -mind - 0.01 * min(cheb(ox, oy, rx, ry) for rx, ry in resources)
            best_res_score = max(best_res_score, 100 * fallback)
        # Slight directional preference to reduce dithering: toward the closest currently available resource.
        closest = min(resources, key=lambda p: cheb(sx, sy, p[0], p[1]))
        bias = -cheb(nx, ny, closest[0], closest[1])
        total = best_res_score + 0.001 * bias
        if total > best_overall:
            best_overall, best_move = total, [dx, dy]

    return best_move