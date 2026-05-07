def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    res_list = [tuple(r) for r in resources]
    res_set = set(res_list)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res_set:
            return [dx, dy]

    def best_reach_dist(x, y):
        if not res_list:
            return 10**9
        d = 10**9
        for rx, ry in res_list:
            k = cheb(x, y, rx, ry)
            if k < d:
                d = k
        return d

    my_best = best_reach_dist(sx, sy)
    opp_best = best_reach_dist(ox, oy)
    cur_adv = opp_best - my_best

    t = observation.get("turn_index", 0)
    pref = [(1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1),(0,0)]
    kshift = t % len(pref)

    best_move = [0, 0]
    best_val = -10**18
    for i in range(len(pref)):
        dx, dy = pref[(i + kshift) % len(pref)]
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd = best_reach_dist(nx, ny)
        oppd = best_reach_dist(ox, oy)
        adv = oppd - myd

        nearest_my = 10**9
        for rx, ry in res_list:
            k = cheb(nx, ny, rx, ry)
            if k < nearest_my:
                nearest_my = k
        nearest_oppp = 10**9
        for rx, ry in res_list:
            k = cheb(ox, oy, rx, ry)
            if k < nearest_oppp:
                nearest_oppp = k

        val = (adv * 1000) + (opp_best - nearest_oppp) * 10 - nearest_my
        if cur_adv <= 0 and adv > 0:
            val += 200000  # decisive switch to races
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move