def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    res_list = sorted((tuple(r) for r in resources), key=lambda p: (p[0], p[1]))

    if not res_list:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            key = (cheb(nx, ny, tx, ty), dx, dy)
            if key < best:
                best = key
        return [best[1], best[2]] if best[0] < 10**18 else [0, 0]

    opp_dist_cache = {}
    for rx, ry in res_list:
        opp_dist_cache[(rx, ry)] = cheb(ox, oy, rx, ry)

    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Choose move that maximizes advantage on the best available resource.
        # Advantage: opponent distance - our distance (bigger is better).
        best_adv = -10**9
        best_res = res_list[0]
        for rx, ry in res_list:
            my_d = cheb(nx, ny, rx, ry)
            adv = opp_dist_cache[(rx, ry)] - my_d
            if adv > best_adv or (adv == best_adv and (rx, ry) < best_res):
                best_adv = adv
                best_res = (rx, ry)

        rx, ry = best_res
        my_d = cheb(nx, ny, rx, ry)

        # Risk control: avoid moving into a spot where opponent is also much closer
        # to that same target after our move (reduces swing effectiveness).
        opp_d = opp_dist_cache[(rx, ry)]
        risk = (my_d + 1) - (opp_d)  # positive means we are relatively worse at that target

        # Slight preference for keeping options open: closer to nearest resource overall.
        my_nearest = 10**9
        for r2 in res_list[:6]:
            my_nearest = min(my_nearest, cheb(nx, ny, r2[0], r2[1]))

        # Deterministic tie-break: prefer lexicographically smaller resource then move.
        key = (-best_adv, risk, my_nearest, rx, ry, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]] if best_key is not None else [0, 0]