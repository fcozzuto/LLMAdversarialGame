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
        best = None
        bestv = -10**9
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            v = -d
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        self_opp_dist = abs(nx - ox) + abs(ny - oy)
        best_adv = -10**18
        for rx, ry in resources:
            self_d = abs(nx - rx) + abs(ny - ry)
            opp_d = abs(ox - rx) + abs(oy - ry)
            adv = opp_d - self_d
            if adv > best_adv:
                best_adv = adv

        # prioritize contested advantage; also keep away from opponent to slow their grabs
        val = best_adv * 100 - self_opp_dist
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]