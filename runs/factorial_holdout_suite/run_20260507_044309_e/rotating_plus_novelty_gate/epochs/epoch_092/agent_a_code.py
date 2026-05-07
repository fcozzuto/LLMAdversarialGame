def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]
    rset = set(resources)
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if (sx, sy) in rset:
        return [0, 0]

    def eval_pos(x, y):
        if not inb(x, y):
            return -10**18
        if (x, y) in rset:
            return 10**12
        if not resources:
            return -cheb(x, y, ox, oy)
        best_adv = -10**18
        best_sd = 10**18
        for rx, ry in resources:
            sd = cheb(x, y, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_adv or (adv == best_adv and sd < best_sd):
                best_adv = adv
                best_sd = sd
        # Prefer moves that keep improving relative advantage; lightly favor reducing absolute distance to the chosen best resource.
        return best_adv * 100 - best_sd - 0.1 * cheb(x, y, ox, oy)

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        v = eval_pos(nx, ny)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
    return [best_move[0], best_move[1]]