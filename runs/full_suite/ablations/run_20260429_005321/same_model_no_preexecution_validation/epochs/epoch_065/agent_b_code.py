def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}
    res = [(int(p[0]), int(p[1])) for p in resources]

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)
    def near_obs(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs: c += 1
        return c

    # Candidate next positions (deterministic order)
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    # If no resources, head away from opponent while minimizing obstacle adjacency
    if not res:
        best = None
        for dx, dy, nx, ny in cand:
            opp_d = cheb(nx, ny, ox, oy)
            o_pen = cheb(nx, ny, ox, oy) <= 1
            score = opp_d*10 - near_obs(nx, ny)*2 - (1 if o_pen else 0)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    best = None
    for dx, dy, nx, ny in cand:
        my_best_adv = -10**18
        my_best_d = 10**18
        for rx, ry in res:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # positive means we're closer than opponent to that resource
            if adv > my_best_adv or (adv == my_best_adv and myd < my_best_d):
                my_best_adv = adv
                my_best_d = myd
        opp_close = 1 if cheb(nx, ny, ox, oy) <= 1 else 0
        # Encourage taking advantage; prefer lower my distance; avoid obstacles and tight proximity to opponent
        score = my_best_adv*100 - my_best_d - near_obs(nx, ny)*2 - opp_close*3
        if best is None or score > best[0]:
            best = (score, dx, dy)
    return [best[1], best[2]]