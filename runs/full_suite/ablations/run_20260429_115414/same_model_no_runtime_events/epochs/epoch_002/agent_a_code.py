def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    sd = (sx, sy)
    od = (ox, oy)

    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ssteps = abs(rx - sx) + abs(ry - sy)
        osteps = abs(rx - ox) + abs(ry - oy)
        # Prefer races we can win; still allow close alternatives.
        win = (osteps - ssteps)
        # Tie-break deterministically by position.
        tie = -((rx * 31 + ry) % 1000003)
        key = (win, -ssteps, tie)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_mkey = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        n_sdist = abs(tx - nx) + abs(ty - ny)
        n_odist = abs(tx - ox) + abs(ty - oy)
        adv = (n_odist - n_sdist)

        # Penalize letting opponent also improve their position vs the target.
        o_improve = abs(tx - ox) + abs(ty - oy) - (abs(tx - (ox + 0)) + abs(ty - (oy + 0)))
        # Approximate opponent next capability: if opponent can reach in <= ours, avoid.
        opp_can = abs(tx - ox) + abs(ty - oy) <= n_sdist

        # Keep some separation from opponent to reduce contention/accidental block.
        sep = cheb(nx, ny, ox, oy)
        sep_pen = -sep

        # Strong preference for moving to cells that reduce our distance to target.
        close_gain = (abs(tx - sx) + abs(ty - sy)) - n_sdist

        key = (adv, close_gain, -int(opp_can), sep_pen, -((nx * 37 + ny) % 1000003))
        if best_mkey is None or key > best_mkey:
            best_mkey = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]