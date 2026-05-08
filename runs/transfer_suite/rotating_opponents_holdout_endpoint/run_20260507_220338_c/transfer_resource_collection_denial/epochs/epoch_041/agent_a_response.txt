def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    res_set = set(tuple(r) for r in resources)
    res_list = [p for p in res_set if p not in obstacles]
    if not res_list:
        return [0, 0]

    best_val = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell_is_res = 1 if (nx, ny) in res_set else 0
        # Evaluate move by best contest against any resource from the next cell.
        local_best = -10**18
        for rx, ry in res_list:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # race>0 => we are closer; myd small => quick payoff.
            race = opd - myd
            val = race * 220 - myd * 6
            if myd == 0:
                val += 1200
            # encourage aiming at a resource even if not immediate
            val += 40 if race >= 1 else 0
            if val > local_best:
                local_best = val

        # Prefer grabbing immediately; otherwise prefer the move that maximizes contest value.
        total = local_best + cell_is_res * 300
        if total > best_val or (total == best_val and (dx, dy) < best_move):
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]