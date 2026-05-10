def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    resources = [tuple(r) for r in observation.get("resources", []) if tuple(r) not in obstacles]
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    my = (sx, sy)
    opp = (ox, oy)

    best = None
    best_key = None
    for r in resources:
        dS = cheb(my, r)
        dO = cheb(opp, r)
        lead = 1 if dS < dO else 0
        key = (lead, dO - dS, -dS, -r[0], -r[1])
        if best_key is None or key > best_key:
            best_key = key
            best = r
    tx, ty = best

    def step_toward(pos):
        x, y = pos
        bestd = None
        bestm = (0, 0)
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = cheb((nx, ny), (tx, ty))
            if bestd is None or d < bestd or (d == bestd and (dx, dy) < bestm):
                bestd = d
                bestm = (dx, dy)
        return bestm if bestd is not None else (0, 0)

    opp_dxdy = step_toward(opp)
    n_ox, n_oy = ox + opp_dxdy[0], oy + opp_dxdy[1]
    opp_after_pos = (n_ox, n_oy)

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_after = (nx, ny)
        my_d = cheb(my_after, (tx, ty))
        opp_d = cheb(opp_after_pos, (tx, ty))
        val = (1 if my_after == (tx, ty) else 0, opp_d - my_d, -my_d, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]