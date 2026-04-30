def choose_move(observation):
    W = observation["grid_width"]; H = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))
    res = []
    for p in resources:
        if p and len(p) >= 2:
            t = (p[0], p[1])
            if t not in obs:
                res.append(t)

    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def cheb(a, b, c, d):
        dx = a - c; dx = -dx if dx < 0 else dx
        dy = b - d; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not res:
        bestd = -10**9; best = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                d = cheb(nx, ny, ox, oy)
                if d > bestd:
                    bestd = d; best = (dx, dy)
        return [best[0], best[1]]

    best_score = -10**18; best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        score = 0
        on_res = (nx, ny) in set(res)
        if on_res:
            score += 10**6

        my_best_adv = -10**9
        opp_best_adv = 10**9
        min_my = 10**9
        min_opp = 10**9
        for rx, ry in res:
            dm = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - dm
            if adv > my_best_adv:
                my_best_adv = adv
            if dm < min_my:
                min_my = dm
            if do < min_opp:
                min_opp = do
            if adv < opp_best_adv:
                opp_best_adv = adv

        score += my_best_adv * 2000
        score += (min_opp - min_my) * 50

        # Avoid letting opponent be much closer to any remaining resource
        score += max(-2000, -opp_best_adv * 20)

        # Small bias toward staying away from obstacles is implicit; also prefer center-ish to reduce edge traps
        score += -abs(nx - (W - 1) / 2) - abs(ny - (H - 1) / 2)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]