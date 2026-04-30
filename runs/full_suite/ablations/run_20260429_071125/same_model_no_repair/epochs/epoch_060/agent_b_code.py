def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    res = [(x, y) for (x, y) in resources if inb(x, y) and (x, y) not in obstacles]
    if not res:
        best = None
        bestv = -10**9
        for dx, dy, nx, ny in legal:
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    t = observation.get("turn_index", 0)
    # deterministic preference: alternate between two "tiers" of resources by parity
    parity = t & 1
    tier_res = [r for i, r in enumerate(res) if (i & 1) == parity]
    if not tier_res:
        tier_res = res

    best_move = None
    best_val = -10**18

    # Aim to increase the distance advantage vs opponent on a promising target
    for dx, dy, nx, ny in legal:
        best_adv = -10**18
        best_self_dist = 10**9
        best_opp_dist = 10**9
        # Choose target that maximizes (opp_dist - self_dist), with secondary preferences
        for rx, ry in tier_res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_adv:
                best_adv = adv
                best_self_dist = sd
                best_opp_dist = od
            elif adv == best_adv:
                if sd < best_self_dist:
                    best_self_dist = sd
                    best_opp_dist = od
                elif sd == best_self_dist and od < best_opp_dist:
                    best_opp_dist = od

        # Small tie-breaker: prefer moving closer to some resource and away from opponent when equal
        nearest_self = best_self_dist
        nearest_opp = cheb(nx, ny, ox, oy)
        val = (best_adv * 1000) - nearest_self - (nearest_opp * 0.01)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]