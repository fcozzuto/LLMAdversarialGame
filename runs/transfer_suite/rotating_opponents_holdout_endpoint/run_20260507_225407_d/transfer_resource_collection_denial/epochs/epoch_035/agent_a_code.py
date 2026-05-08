def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            self_c = abs(nx - tx) + abs(ny - ty)
            opp_c = abs(nx - ox) + abs(ny - oy)
            v = -self_c + 0.05 * opp_c
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        my_best_adv = -10**18
        my_best_selfd = 10**18
        for rx, ry in resources:
            self_d = abs(nx - rx) + abs(ny - ry)
            opp_d = abs(ox - rx) + abs(oy - ry)
            adv = opp_d - self_d
            if adv > my_best_adv or (adv == my_best_adv and self_d < my_best_selfd):
                my_best_adv = adv
                my_best_selfd = self_d
        v = my_best_adv - 0.02 * my_best_selfd
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]