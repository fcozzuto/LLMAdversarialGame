def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    resources_raw = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []

    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in resources_raw:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        best = (-10**18, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            val = (abs(nx - ox) + abs(ny - oy))
            cand = (val, -abs(nx - ox), -abs(ny - oy), dx, dy)
            if cand > best:
                best = cand
        return [best[3], best[4]]

    best_targets = []
    for tx, ty in resources:
        d_self = abs(tx - sx) + abs(ty - sy)
        d_opp = abs(tx - ox) + abs(ty - oy)
        if d_self <= d_opp - 1:
            best_targets.append((tx, ty, d_self, d_opp))
    if best_targets:
        # Take closest guaranteed-win target; deterministic tie by (tx,ty)
        best_targets.sort(key=lambda t: (t[2], t[0], t[1]))
        tx, ty, _, _ = best_targets[0]
    else:
        # No guaranteed advantage: pick target far from opponent while not too far from us.
        # Deterministic tie by (tx,ty)
        best = None
        for tx, ty in resources:
            d_self = abs(tx - sx) + abs(ty - sy)
            d_opp = abs(tx - ox) + abs(ty - oy)
            val = (d_opp - d_self, -d_self)  # prioritize opponent-distant and then self-close
            cand = (val, tx, ty)
            if best is None or cand > best:
                best = cand
        tx, ty = best[1], best[2]

    best_move = (None, None, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        new_d_self = abs(tx - nx) + abs(ty - ny)
        new_d_opp = abs(tx - ox) + abs(ty - oy)  # opp static this turn
        # Small tie-break: prefer moving toward the target and away from opponent a bit.
        val = (-new_d_self, (new_d_opp - new_d_self), -abs(nx - ox) - abs(ny - oy), -dx, -dy, dx, dy)
        if val > best_move[2] if isinstance(best_move[2], tuple) else True:
            best_move = (nx, ny, val)

    dx, dy = best_move[0], best_move[1]
    # best_move stores val tuple; dx,dy are last two in val
    res_dx, res_dy = best_move[2][-2], best_move[2][-1]
    return [res_dx, res_dy]