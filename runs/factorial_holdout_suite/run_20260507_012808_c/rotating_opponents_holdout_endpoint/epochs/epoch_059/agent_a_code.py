def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    my_pos = (sx, sy)
    opp_pos = (ox, oy)

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = sx + dx; ny = sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((dx, dy))
    if not cand:
        return [0, 0]

    best = cand[0]
    best_val = -10**18
    res_set = set(resources)

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        new_my = (nx, ny)
        val = 0
        if new_my in res_set:
            val += 10000  # immediate pickup

        # Choose resource we can beat the opponent to, otherwise just head to closest
        local_best = -10**18
        for r in resources:
            my_d = cheb(new_my, r)
            opp_d = cheb(opp_pos, r)
            # Positive when we are closer or can arrive first
            beat = opp_d - my_d
            # Prefer shorter my_d when beat is similar
            score = beat * 100 - my_d
            if beat >= 1:
                score += 200
            local_best = score if score > local_best else local_best

        # Slightly discourage drifting away when no clear beat exists
        val += local_best
        val += -cheb(new_my, resources[0]) // 8 if resources else 0

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]