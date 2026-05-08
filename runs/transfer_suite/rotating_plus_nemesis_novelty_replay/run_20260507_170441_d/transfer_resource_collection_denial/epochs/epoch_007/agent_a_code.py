def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {tuple(p) for p in obstacles}

    cand = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def obst_clear(x, y):
        if not obstacles:
            return 1000.0
        best = 10**18
        for px, py in obstacles:
            v = (x - px) * (x - px) + (y - py) * (y - py)
            if v < best:
                best = v
        return best

    # Pick a resource where we are relatively closer than the opponent
    best_r = resources[0]
    best_gain = -10**18
    for rx, ry in resources:
        myd = d2(sx, sy, rx, ry)
        opd = d2(ox, oy, rx, ry)
        gain = opd - myd
        if gain > best_gain or (gain == best_gain and (rx, ry) < tuple(best_r)):
            best_gain = gain
            best_r = [rx, ry]
    tx, ty = best_r

    # Evaluate one-step moves: prioritize moving toward target while not stepping into/near obstacles
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            val = -10**12
        else:
            my_dist = d2(nx, ny, tx, ty)
            my_next_gain = d2(nx, ny, tx, ty)
            # Also consider denial: keep opponent farther from the same target
            opp_dist = d2(ox, oy, tx, ty)
            clear = obst_clear(nx, ny)
            # Higher is better
            val = (-my_dist) + (0.001 * clear) + (0.0005 * (opp_dist - my_dist))
        if val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val = val
            best_move = [dx, dy]

    # If all moves invalid/obstructed, stay put deterministically
    if best_val < -10**11:
        return [0, 0]
    return best_move