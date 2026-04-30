def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obst.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist_cheb(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    opp_pos = (ox, oy)

    if not resources:
        best = legal[0]; bestv = -10**18
        for dx, dy in legal:
            my_pos = (sx + dx, sy + dy)
            # maximize distance from opponent, then toward center
            dmo = dist_cheb(my_pos, opp_pos)
            center = abs((sx + dx) - (w - 1) / 2.0) + abs((sy + dy) - (h - 1) / 2.0)
            v = 1000 * dmo - center
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    best = legal[0]; bestv = -10**18
    for dx, dy in legal:
        my_pos = (sx + dx, sy + dy)
        my_min = 10**9
        opp_min = 10**9
        win_here = 0
        for r in resources:
            dmy = dist_cheb(my_pos, r)
            dop = dist_cheb(opp_pos, r)
            if dmy < my_min: my_min = dmy
            if dop < opp_min: opp_min = dop
            if dmy == 0: win_here = 1
        advantage = opp_min - my_min
        dmo = dist_cheb(my_pos, opp_pos)
        # Prefer grabbing (dmy==0), then outpacing opponent to some resource, avoid moving too close if tie
        v = 20000 * win_here + 120 * advantage + 3 * dmo - 2 * my_min
        if v > bestv:
            bestv = v; best = (dx, dy)
    return [best[0], best[1]]