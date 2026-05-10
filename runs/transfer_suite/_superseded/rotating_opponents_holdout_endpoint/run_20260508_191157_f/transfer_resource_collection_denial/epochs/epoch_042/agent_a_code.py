def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obs_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        key = (od - sd, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def next_cell(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            return None
        if (nx, ny) in obs_set:
            return None
        return nx, ny

    candidates = []
    for dx, dy in moves:
        nc = next_cell(dx, dy)
        if nc is None:
            continue
        nx, ny = nc
        nd_t = abs(tx - nx) + abs(ty - ny)
        ns = abs(tx - sx) + abs(ty - sy)
        no_d = abs(tx - ox) + abs(ty - oy)
        n_self = abs(tx - nx) + abs(ty - ny)
        n_opp = abs(tx - ox) + abs(ty - oy)
        adv = n_opp - n_self
        toward = -nd_t
        # Primary: gain over opponent; Secondary: closer to target; Tertiary: keep distance to opponent
        score = adv * 1000 + toward * 3 + (no_d - n_opp) * 2 + (ns - n_self)
        candidates.append((score, -dx, -dy, dx, dy))

    if candidates:
        candidates.sort(reverse=True)
        return [candidates[0][3], candidates[0][4]]

    # If all moves blocked/out of bounds: stay put deterministically
    return [0, 0]