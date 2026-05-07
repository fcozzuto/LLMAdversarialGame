def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    occ = set((x, y) for x, y in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_dir_to(tx, ty):
        deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        best = None
        best_d = 10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in occ:
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best_d:
                best_d = d
                best = [dx, dy]
        if best is not None:
            return best
        return [0, 0]

    if not resources:
        return [0, 0]

    best_opp_d = 10**9
    opp_target = resources[0]
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if d < best_opp_d:
            best_opp_d = d
            opp_target = (rx, ry)

    # Choose a resource to contest if possible; otherwise maximize arrival advantage.
    chosen = None
    contestable = []
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if ds <= do:
            contestable.append((ds, rx, ry))
    if contestable:
        contestable.sort(key=lambda t: (t[0], t[1], t[2]))
        _, tx, ty = contestable[0]
        chosen = (tx, ty)
    else:
        best_adv = -10**9
        best_ds = 10**9
        tx, ty = resources[0]
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if adv > best_adv or (adv == best_adv and (ds < best_ds or (ds == best_ds and (rx, ry) < (tx, ty)))):
                best_adv = adv
                best_ds = ds
                tx, ty = rx, ry
        chosen = (tx, ty)

    # If target cell is currently blocked, fall back to opponent-target or stay-near resource.
    if chosen in occ:
        tx, ty = opp_target
        if (tx, ty) in occ:
            tx, ty = resources[0]
        chosen = (tx, ty)

    return best_dir_to(chosen[0], chosen[1])