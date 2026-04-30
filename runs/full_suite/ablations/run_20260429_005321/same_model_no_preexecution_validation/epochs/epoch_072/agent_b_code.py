def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    res = [(int(x), int(y)) for x, y in (observation.get("resources") or [])]
    obstacles = {(int(x), int(y)) for x, y in (observation.get("obstacles") or [])}

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy

    def near_obs(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obstacles:
                c += 1
        return c

    # If no resources, move to increase distance from opponent while avoiding obstacles.
    if not res:
        bestv = -10**18; bestm = [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            v = 1.1 * cheb(nx, ny, ox, oy) - 0.5 * near_obs(nx, ny)
            if v > bestv:
                bestv = v; bestm = [dx, dy]
        return bestm

    # Choose move that maximizes immediate capture likelihood and relative advantage.
    bestv = -10**18; bestm = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        myd_opp = cheb(nx, ny, ox, oy)
        v = -0.08 * myd_opp - 0.35 * near_obs(nx, ny)

        # Resource-related value: best advantage over all remaining resources.
        if (nx, ny) in set(res):
            v += 2_000_000  # immediate collection if resource occupies destination
        best_adv = -10**18
        best_res_score = 0
        for rx, ry in res:
            myd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - myd  # positive if we can reach sooner
            # Tie-break: prefer closer and higher immediate safety toward opponent.
            tieb = -0.02 * myd - 0.01 * myd_opp + (1.0 / (1 + cheb(nx, ny, rx, ry)))
            score = adv + tieb
            if score > best_res_score:
                best_res_score = score
                best_adv = adv
        v += 1200 * best_res_score
        # Slight preference to reduce our distance to the chosen best resource.
        v += 0.6 * best_adv

        if v > bestv:
            bestv = v; bestm = [dx, dy]
    return bestm