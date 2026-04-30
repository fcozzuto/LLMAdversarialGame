def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)
    resources = observation.get("resources") or []
    res = [tuple(p) for p in resources]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not res:
        tx = 0 if ox > sx else w - 1
        ty = 0 if oy > sy else h - 1
        best = (0, 0)
        bestv = -10**9
        for dx, dy, nx, ny in legal:
            v = cheb(nx, ny, tx, ty) - 0.25 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = -10**18
    cur_do = cheb(sx, sy, ox, oy)

    for dx, dy, nx, ny in legal:
        # Base: get closer to our chosen resource
        # Resource choice: prefer ones we're closer to than opponent (or at least not much worse).
        best_r = 10**9
        best_adv = -10**9
        for rx, ry in res:
            d_me = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # also account opponent after our move (they might move closer later); approximate with current opp dist
            # advantage: how much closer we are than opponent
            adv = (cheb(sx, sy, rx, ry) - cheb(ox, oy, rx, ry)) - (d_me - cheb(sx, sy, rx, ry)) * 0.1
            if d_me < best_r or (d_me == best_r and adv > best_adv):
                best_r = d_me
                best_adv = adv
        # Avoid stepping into opponent "catch" territory: penalize if we reduce distance to opponent a lot.
        dn = cheb(nx, ny, ox, oy)
        approach_pen = 0.0
        if dn < cur_do:
            approach_pen = (cur_do - dn) * 2.0
        # Strong preference to be at/near a resource
        collect_bonus = 0.0
        if (nx, ny) in res:
            collect_bonus = 50.0
        # Slight preference for moves that reduce our distance to opponent's likely contest resources
        contest_pen = 0.0
        for rx, ry in res:
            if cheb(nx, ny, rx, ry) <= 1 and cheb(ox, oy, rx, ry) <= 1:
                contest_pen += 1.5
        val = (-best_r) + best_adv * 1.3 - approach_pen + collect_bonus - contest_pen
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]