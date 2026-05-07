def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2; ax = -ax if ax < 0 else ax
        ay = y1 - y2; ay = -ay if ay < 0 else ay
        return ax if ax > ay else ay

    res_list = [tuple(r) for r in resources]
    res_set = set(res_list)

    best_move = [0, 0]
    best_score = -10**18

    # Immediate grab if possible
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res_set:
            return [dx, dy]

    if not res_list:
        # No resources visible: head toward opponent line (deterministic fallback)
        # prefer decreasing cheb distance to opponent
        bestd = 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            if d < bestd:
                bestd = d; best_move = [dx, dy]
        return best_move

    # Evaluate each candidate move by maximizing "arrive earlier" margin to any resource
    # margin = (opponent_dist - our_dist)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        our_best_adv = -10**18
        our_closest = 10**18
        for rx, ry in res_list:
            od = cheb(ox, oy, rx, ry)
            nd = cheb(nx, ny, rx, ry)
            adv = od - nd
            if adv > our_best_adv:
                our_best_adv = adv
            if nd < our_closest:
                our_closest = nd

        # Prefer positive advantage; if none, minimize our_closest.
        # Tie-break deterministically with smaller cheb to opponent (safer positioning).
        score = our_best_adv * 10**6 - our_closest * 10 - cheb(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move