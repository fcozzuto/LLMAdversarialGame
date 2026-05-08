def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    res_list = [tuple(r) for r in resources if tuple(r) not in obstacles]
    if not res_list:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax >= ay else ay

    best_move = (0, 0, -10**9)
    # Prefer staying/advancing toward a resource we can reach before opponent,
    # with a small intercept bonus for resources on/near opponent's current row.
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        best_score = -10**9
        for rx, ry in res_list:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            intercept_bonus = 0
            if ry == oy:
                intercept_bonus = 0.6
            elif abs(ry - oy) == 1:
                intercept_bonus = 0.25
            lead = opd - myd  # positive means we are closer
            # tie-break: closer to the resource (smaller myd) and more lead
            score = lead * 10 + intercept_bonus - myd * 0.05
            if score > best_score:
                best_score = score
        if best_score > best_move[2]:
            best_move = (dx, dy, best_score)
    return [int(best_move[0]), int(best_move[1])]