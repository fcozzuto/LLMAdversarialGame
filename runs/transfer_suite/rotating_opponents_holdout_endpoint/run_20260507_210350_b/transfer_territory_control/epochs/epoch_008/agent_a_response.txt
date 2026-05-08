def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    obstacles = observation.get("obstacles") or []
    def to_set(v):
        s = set()
        if v:
            for p in v:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    s.add((int(p[0]), int(p[1])))
        return s
    obs = to_set(obstacles)
    self_set = to_set(observation.get("self_territory"))
    opp_set = to_set(observation.get("opponent_territory"))
    unclaimed = to_set(observation.get("unclaimed_cells"))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def count_adj(sset, x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in sset:
                c += 1
        return c

    myc = int(observation.get("self_territory_count", 0))
    oppc = int(observation.get("opponent_territory_count", 0))
    want_attack = myc <= oppc

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obs:
            score = -10**12
        else:
            if (nx, ny) in opp_set:
                base = 2.6
            elif (nx, ny) in unclaimed:
                base = 1.2
            elif (nx, ny) in self_set:
                base = 0.3
            else:
                base = 0.0
            adj_un = count_adj(unclaimed, nx, ny)
            adj_self = count_adj(self_set, nx, ny)
            adj_obs = count_adj(obs, nx, ny)
            d_opp = abs(nx - ox) + abs(ny - oy)
            d_now = abs(sx - ox) + abs(sy - oy)
            dist_term = (d_now - d_opp) if want_attack else (d_opp - d_now)
            score = (base + 0.08 * adj_un + 0.18 * adj_self - 0.25 * adj_obs + 0.05 * dist_term)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]