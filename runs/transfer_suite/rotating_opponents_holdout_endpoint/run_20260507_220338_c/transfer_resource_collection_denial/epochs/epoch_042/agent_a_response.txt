def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx >= dy else dy

    res_set = set(tuple(r) for r in resources if tuple(r) not in obstacles)
    res_list = list(res_set)
    if not res_list:
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_gain = 0
        # Favor resources where we are closer; also prefer capturing ones very near now.
        for rx, ry in res_list:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Score: win margin scaled, plus faster-to-reach preference
            # If we are currently farther, discourage (still allow blocking by small weight).
            margin = opd - myd
            val = margin * 180 - myd * 5
            # If opponent can reach immediately next, penalize a bit to avoid handing turns back.
            if opd <= 1 and myd > opd:
                val -= 60
            # Slight extra if stepping onto a resource.
            if (nx, ny) == (rx, ry):
                val += 120
            if val > my_gain:
                my_gain = val

        # Minor tie-break: avoid moving away from the currently best resource
        # by using distance to best candidate resource.
        # Deterministic: recompute best resource by same heuristic at current next cell.
        anchor_val = -10**18
        anchor_dist = 10**9
        for rx, ry in res_list:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            margin = opd - myd
            val = margin * 180 - myd * 5
            if val > anchor_val or (val == anchor_val and myd < anchor_dist):
                anchor_val = val; anchor_dist = myd

        # Opponent-shape penalty: prefer moves that increase distance to opponent slightly.
        opp_dist = cheb(nx, ny, ox, oy)
        cur_opp_dist = cheb(sx, sy, ox, oy)
        opp_bonus = (opp_dist - cur_opp_dist) * 2

        total = my_gain + opp_bonus - (cheb(nx, ny, sx, sy) * 0)  # keep deterministic structure
        if total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]