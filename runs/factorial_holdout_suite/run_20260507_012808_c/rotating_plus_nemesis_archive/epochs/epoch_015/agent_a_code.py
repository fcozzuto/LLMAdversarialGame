def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    occ = set((x, y) for x, y in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Opponent likely target: nearest in Chebyshev metric.
    opp_target = resources[0]
    best_od = cheb(ox, oy, resources[0][0], resources[0][1])
    for rx, ry in resources[1:]:
        d = cheb(ox, oy, rx, ry)
        if d < best_od:
            best_od = d
            opp_target = (rx, ry)

    # Choose target: either contest their target if we can arrive no later,
    # else go for best resource that maximizes distance advantage over them.
    tx, ty = opp_target
    ds_self = cheb(sx, sy, tx, ty)
    if ds_self <= best_od:
        chosen = (tx, ty)
    else:
        chosen = resources[0]
        best_adv = -10**9
        best_tieb = 10**9
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = (do - ds)  # positive => we are closer
            tieb = ds
            if adv > best_adv or (adv == best_adv and tieb < best_tieb):
                best_adv = adv
                best_tieb = tieb
                chosen = (rx, ry)

    tx, ty = chosen

    # Greedy move with simple obstacle detour: prefer moves that reduce our distance to target.
    best = (10**9, 10**9, 0, 0)  # (dist, opp_dist, dx, dy) with lexicographic preference
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        d = cheb(nx, ny, tx, ty)
        od = cheb(nx, ny, ox, oy)
        cand = (d, -od, dx, dy)
        if cand < best:
            best = cand

    # If all moves blocked (unlikely), stay.
    if best[2] == 0 and best[3] == 0 and (sx, sy) in occ:
        return [0, 0]
    return [best[2], best[3]]