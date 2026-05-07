def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    # Greedy target scoring from a hypothetical position
    def best_target_score(x, y):
        best_sc = -10**18
        for rx, ry in resources:
            sd = man(x, y, rx, ry)
            od = man(x, y, rx, ry) if (rx, ry) == (ox, oy) else man(ox, oy, rx, ry)
            # If resource is closer to opponent than us, heavily discourage.
            # If tie, prefer closer resource for us.
            adv = (od - sd)
            sc = adv * 1000 - sd
            if sc > best_sc:
                best_sc = sc
        return best_sc

    # One-step lookahead with obstacle-aware tie breaking
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Prefer moves that reduce our distance to some favorable target
        base = best_target_score(nx, ny)

        # Small deterministic penalty for moving adjacent to obstacles (risk of denier trapping)
        adj_pen = 0
        for ox2, oy2 in obstacles:
            if man(nx, ny, ox2, oy2) == 1:
                adj_pen += 6
        # Tiny bias to progress toward opponent-advantaged direction (toward resources)
        prog_bias = 0
        if resources:
            # choose the resource that is currently best for us at next pos
            # (ties resolved deterministically by list order)
            best_r = resources[0]
            best_local = -10**18
            for r in resources:
                rx, ry = r
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                sc = (od - sd) * 1000 - sd
                if sc > best_local:
                    best_local = sc
                    best_r = r
            prog_bias = -man(nx, ny, best_r[0], best_r[1]) // 2

        val = base - adj_pen + prog_bias
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    if not valid(sx + best_move[0], sy + best_move[1]):
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]