def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
    resset = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resset.add((int(p[0]), int(p[1])))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs
    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def best_moves_target(tx, ty):
        # choose a step that minimizes dist to (tx,ty), tie-break prefer increasing x then y deterministically
        bestd = 10**9
        best = (0, 0)
        for dx0, dy0 in deltas:
            nx, ny = x + dx0, y + dy0
            if not inb(nx, ny):
                continue
            d = max(abs(nx - tx), abs(ny - ty))
            if d < bestd or (d == bestd and (dx0, dy0) < best):
                bestd = d
                best = (dx0, dy0)
        return list(best)

    if resources:
        # compute opponent nearest distances to each resource
        mypos = (x, y)
        opp = (ox, oy)
        best_move = [0, 0]
        best_val = -10**18
        for dx0, dy0 in deltas:
            nx, ny = x + dx0, y + dy0
            if not inb(nx, ny):
                continue
            myd_best = 10**9
            oppd_best = 10**9
            immediate = 1 if (nx, ny) in resset else 0
            for rx, ry in resset:
                dmy = dist((nx, ny), (rx, ry))
                if dmy < myd_best:
                    myd_best = dmy
                dpo = dist(opp, (rx, ry))
                if dpo < oppd_best:
                    oppd_best = dpo
            # prefer immediate picks, then being closer than opponent, then progress toward nearest
            opp_adv = oppd_best - myd_best
            center = (nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2
            val = immediate * 1000 + opp_adv * 10 - myd_best - 0.001 * center
            if val > best_val or (val == best_val and (dx0, dy0) < (best_move[0], best_move[1])):
                best_val = val
                best_move = [dx0, dy0]
        return best_move

    # No visible resources: drift toward center while keeping some distance from opponent.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = [0, 0]
    best_val = -10**18
    for dx0, dy0 in deltas:
        nx, ny = x + dx0, y + dy0
        if not inb(nx, ny):
            continue
        dcenter = dist((nx, ny), (cx, cy))
        dopp = dist((nx, ny), (ox, oy))
        val = dopp * 0.5 - dcenter
        if val > best_val or (val == best_val and (dx0, dy0) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx0, dy0]
    return best_move