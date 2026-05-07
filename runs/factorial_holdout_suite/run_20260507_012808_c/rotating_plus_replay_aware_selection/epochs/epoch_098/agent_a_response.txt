def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d < bestd:
                    bestd = d
                    best = [dx, dy]
        return best

    res = [tuple(r) for r in resources]
    # Deterministically maximize our relative progress to the best contestable resource.
    best_move = [0, 0]
    best_score = -10**9
    best_t = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Choose the resource where this move gives the largest opponent-distance advantage.
        top_adv = -10**9
        top_res = None
        for rx, ry in res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if adv > top_adv:
                top_adv = adv
                top_res = (rx, ry)
            elif adv == top_adv and top_res is not None:
                # tie-break toward smaller our distance, then toward lexicographically smaller resource
                sdb = cheb(nx, ny, top_res[0], top_res[1])
                if sd < sdb or (sd == sdb and (rx, ry) < top_res):
                    top_res = (rx, ry)
        # Primary: maximize top_adv. Secondary: minimize our distance to that selected resource.
        if top_res is None:
            continue
        ourd = cheb(nx, ny, top_res[0], top_res[1])
        key = (top_adv, -ourd, -abs(ox - nx) - abs(oy - ny))
        best_key = None
        # Recompute current best key style for comparison deterministically
        if best_t is None:
            best_key = (-10**9, 10**9, 0)
        else:
            best_adv, best_our = best_score, cheb(sx + best_move[0], sy + best_move[1], best_t[0], best_t[1])
            best_key = (best_adv, -best_our, 0)
        cand_key = key
        if best_t is None or cand_key > best_key:
            best_score = top_adv
            best_move = [dx, dy]
            best_t = top_res

    return best_move