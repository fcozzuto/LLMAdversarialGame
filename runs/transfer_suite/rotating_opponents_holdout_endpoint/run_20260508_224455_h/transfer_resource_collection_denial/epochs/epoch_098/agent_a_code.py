def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    res = []
    for r in resources:
        x, y = int(r[0]), int(r[1])
        if inb(x, y) and (x, y) not in obs:
            res.append((x, y))
    if not res:
        return [0, 0]

    # Focus on a few best candidate resources for speed and determinism
    res.sort(key=lambda p: dist((ox, oy), p) - dist((sx, sy), p))
    res = res[:8]

    best_move = (0, 0)
    best_val = -10**18

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_pos = (nx, ny)
        my_best = -10**18
        for r in res:
            d_my = dist(my_pos, r)
            d_opp = dist((ox, oy), r)
            # Prefer resources where we are closer than opponent; break ties by absolute closeness
            val = (d_opp - d_my) * 100 - d_my
            if val > my_best:
                my_best = val

        # If we can't improve advantage, gently move to reduce my distance to the best resource
        if my_best > best_val:
            best_val = my_best
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]