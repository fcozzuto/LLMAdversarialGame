def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_res = None
    best_adv = -10**9
    # Pick a resource where we have a clear distance advantage; prefer larger advantage, then closer, then deterministic tie.
    for r in resources:
        rx, ry = r
        if (rx, ry) in obs_set:
            continue
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        adv = od - sd
        if adv > best_adv:
            best_adv = adv
            best_res = (rx, ry)
        elif adv == best_adv and best_res is not None:
            brx, bry = best_res
            bsd = abs(brx - sx) + abs(bry - sy)
            if sd < bsd or (sd == bsd and (rx, ry) < (brx, bry)):
                best_res = (rx, ry)

    # If no resources, drift toward center deterministically.
    if best_res is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None; best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set: 
                continue
            d = abs(nx - tx) + abs(ny - ty)
            sc = -d
            if sc > best_score:
                best_score = sc; best = (dx, dy)
        return list(best if best is not None else (0, 0))

    rx, ry = best_res
    # Evaluate each legal move by improving our distance to the target, while also reducing theirs.
    best_move = (0, 0); best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        self_d = abs(rx - nx) + abs(ry - ny)
        opp_d = abs(rx - ox) + abs(ry - oy)
        # Strategic shift: prioritize taking the advantage back by moving toward the chosen target;
        # if we can't, move to reduce nearest-resource distance.
        if resources:
            nearest = 10**9
            for r in resources:
                tx, ty = r
                if (tx, ty) in obs_set:
                    continue
                dd = abs(tx - nx) + abs(ty - ny)
                if dd < nearest:
                    nearest = dd
            if nearest == 10**9:
                nearest = self_d
        else:
            nearest = self_d
        # Higher is better: closer to target, and if we already had disadvantage, still try to maximize advantage.
        sc = (opp_d - self_d) * 3.0 - self_d * 0.7 - nearest * 0.25
        # Deterministic tie-breaker: prefer staying still slightly less to ensure movement.
        if sc > best_score or (sc == best_score and (dx, dy) < best_move):
            best_score = sc; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]