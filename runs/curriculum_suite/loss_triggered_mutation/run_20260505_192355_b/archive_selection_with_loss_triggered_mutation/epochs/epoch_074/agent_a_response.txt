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

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not res:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            # drift toward center
            score = cheb((nx, ny), (w // 2, h // 2))
            key = (score, abs(nx - ox) + abs(ny - oy), dx, dy)
            if best is None or key < best:
                best = key
        return [best[2], best[3]] if best else [0, 0]

    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Choose a target resource where we gain the most advantage over opponent.
        # Advantage prefers resources where self is closer than opponent; ties favor closer self.
        best_t = None
        for rx, ry in res:
            sd = cheb((nx, ny), (rx, ry))
            od = cheb((ox, oy), (rx, ry))
            advantage = od - sd  # positive if we are closer than opponent
            # Small tiebreakers to reduce dithering: prefer lower sd and avoid moving away from opponent
            key_t = (-advantage, sd, -((nx - ox) ** 2 + (ny - oy) ** 2), rx, ry)
            if best_t is None or key_t < best_t:
                best_t = key_t

        # Secondary: prefer moves that also increase opponent distance to that chosen target
        # Approximate by evaluating against the same best target resource derived from best_t.
        # Recover resource deterministically by scanning again for that minimal key_t.
        _, _, _, trx, try_ = best_t
        od_to = cheb((ox, oy), (trx, try_))
        sd_to = cheb((nx, ny), (trx, try_))
        # Prefer: maximize (od_to - sd_to), then minimize our sd, then maximize opponent distance, then toward center.
        primary = -(od_to - sd_to)
        opp_push = od_to
        center_dist = cheb((nx, ny), (w // 2, h // 2))

        key = (primary, sd_to, -opp_push, center_dist, dx, dy)
        if best_key is None or key < best_key:
            best_key = key

    if best_key is None:
        return [0, 0]
    return [best_key[4], best_key[5]]