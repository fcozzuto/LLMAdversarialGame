def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = [0, 0]
        best_sc = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in obstacles:
                continue
            d = abs(nx - ox) + abs(ny - oy)
            if d > best_sc:
                best_sc = d
                best = [dx, dy]
        return best

    def mindist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_res = None
    best_adv = 10**9
    for rx, ry in resources:
        myd = mindist(sx, sy, rx, ry)
        opd = mindist(ox, oy, rx, ry)
        # Prefer resources where we are closer (lower myd-opd), tie-break by absolute closeness and then coordinates
        adv = myd - opd
        if adv < best_adv or (adv == best_adv and (myd < mindist(sx, sy, best_res[0], best_res[1]) if best_res else True)) or (adv == best_adv and myd == mindist(sx, sy, best_res[0], best_res[1]) if best_res else False):
            best_adv = adv
            best_res = [rx, ry]

    tx, ty = best_res
    best_move = [0, 0]
    best_sc = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd = mindist(nx, ny, tx, ty)
        oppd = mindist(nx, ny, ox, oy)
        # Encourage moving toward target and away from opponent; slight preference to keep options open
        sc = (-myd) + 0.35 * oppd
        if (nx, ny) == (tx, ty):
            sc += 1000
        # Deterministic tie-break: smaller dx, then smaller dy
        if sc > best_sc or (sc == best_sc and (dx, dy) < (best_move[0], best_move[1])):
            best_sc = sc
            best_move = [dx, dy]
    return best_move