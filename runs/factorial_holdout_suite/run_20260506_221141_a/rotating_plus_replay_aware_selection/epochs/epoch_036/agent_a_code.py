def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        tx = 0 if sx <= (gw - 1) // 2 else gw - 1
        ty = 0 if sy <= (gh - 1) // 2 else gh - 1
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if legal(sx + dx, sy + dy):
            return [dx, dy]
        if legal(sx + dx, sy):
            return [dx, 0]
        if legal(sx, sy + dy):
            return [0, dy]
        return [0, 0]

    best_val = -10**18
    best = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Prefer moves that create "we are not slower than opponent" to some resource;
        # otherwise, steer to resources where opponent is much farther.
        cand_best = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive means we are closer
            if lead >= 0:
                val = 10**6 + lead * 1000 - ds  # strong pull to reachable/contested wins
            else:
                val = lead * 1000 - ds * 2  # avoid resources where we are clearly behind
            if val > cand_best:
                cand_best = val

        # Tie-break deterministically toward shorter own distance to best resource,
        # approximated by preferring smaller ds among all resources.
        if cand_best > best_val:
            best_val = cand_best
            best = [dx, dy]
        elif cand_best == best_val:
            # second pass: minimize own distance to any resource (deterministic)
            min_ds = min(cheb(nx, ny, r[0], r[1]) for r in resources)
            cur_min_ds = min(cheb(sx + best[0], sy + best[1], r[0], r[1]) for r in resources)
            if min_ds < cur_min_ds:
                best = [dx, dy]

    if legal(sx + best[0], sy + best[1]):
        return best
    return [0, 0]