def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles if len(p) >= 2)

    self_terr = observation.get("self_territory") or []
    selfset = set((int(p[0]), int(p[1])) for p in self_terr if len(p) >= 2)

    opp_terr = observation.get("opponent_territory") or []
    opposet = set((int(p[0]), int(p[1])) for p in opp_terr if len(p) >= 2)

    unclaimed = observation.get("unclaimed_cells") or []
    unq = set((int(p[0]), int(p[1])) for p in unclaimed if len(p) >= 2)

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    opp_list = list(opposet)
    nearest_opp_dist_cache = {}
    def nearest_opp_dist(x, y):
        key = (x, y)
        if key in nearest_opp_dist_cache:
            return nearest_opp_dist_cache[key]
        if not opp_list:
            d = manh(x, y, ox, oy)
        else:
            d = min(manh(x, y, px, py) for px, py in opp_list)
        nearest_opp_dist_cache[key] = d
        return d

    best = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        val = 0.0
        d_opp_pos = manh(nx, ny, ox, oy)

        if (nx, ny) in opposet:
            val += 600.0
            val += max(0, 20 - d_opp_pos) * 2.0
            val -= 0.5 * nearest_opp_dist(nx, ny)
        elif (nx, ny) in unq:
            val += 220.0
            val -= 1.2 * nearest_opp_dist(nx, ny)
            val -= 0.3 * d_opp_pos
        elif (nx, ny) in selfset:
            val += 18.0
            val += 0.05 * d_opp_pos
        else:
            val += 60.0
            val -= 0.8 * nearest_opp_dist(nx, ny)
            val -= 0.2 * d_opp_pos

        # slight preference to reduce oscillation when tied
        val -= 0.01 * (manh(nx, ny, sx, sy))

        cand = (dx, dy)
        if val > best_val or (val == best_val and cand < best):
            best_val = val
            best = cand

    return [int(best[0]), int(best[1])]