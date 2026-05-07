def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if not resources:
        return [0, 0]

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    res_set = set((r[0], r[1]) for r in resources)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_score = -10**18

    res_sorted = sorted(resources, key=lambda r: (r[0], r[1]))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        immediate = 1 if (nx, ny) in res_set else 0
        # Evaluate best guaranteed "race" advantage after this move
        # Advantage = (opponent distance - my distance): higher means I can reach first.
        # Prefer immediate capture strongly.
        adv_best = -10**9
        dist_self_best = 10**9
        target_best = None
        for rx, ry in res_sorted:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if adv > adv_best or (adv == adv_best and (ds < dist_self_best or (ds == dist_self_best and (rx, ry) < target_best))):
                adv_best = adv
                dist_self_best = ds
                target_best = (rx, ry)

        score = immediate * 10**6 + adv_best * 1000 - dist_self_best
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best