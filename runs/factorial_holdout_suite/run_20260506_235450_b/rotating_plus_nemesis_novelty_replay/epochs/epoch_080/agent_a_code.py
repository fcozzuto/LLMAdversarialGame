def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            x, y = p
            obstacles.add((x, y))
        except:
            pass
    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = ox is not None and oy is not None

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    resset = set()
    for r in resources:
        try:
            x, y = r
            resset.add((x, y))
        except:
            pass
    if not resset:
        # Drift toward the nearest edge-corner diagonal away from opponent when no resource is visible
        tx, ty = (0 if sx > w // 2 else w - 1), (0 if sy > h // 2 else h - 1)
        best = (-10**18, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: 
                continue
            sc = -(abs(nx - tx) + abs(ny - ty))
            if sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    # One-step lookahead: choose move that maximizes advantage to the best next-target resource
    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in resset:
            return [dx, dy]
        cur_best = -10**18
        self_adv_tiebreak = 10**18
        for rx, ry in resset:
            sd = abs(rx - nx) + abs(ry - ny)
            if opp_exists:
                od = abs(rx - ox) + abs(ry - oy)
                sc = (od - sd) * 1000 - sd
            else:
                sc = -sd
            if sc > cur_best or (sc == cur_best and sd < self_adv_tiebreak):
                cur_best = sc
                self_adv_tiebreak = sd
        if cur_best > best[0] or (cur_best == best[0] and (dx, dy) < (best[1], best[2])):
            best = (cur_best, dx, dy)
    return [best[1], best[2]]