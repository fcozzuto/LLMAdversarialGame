def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = [(r[0], r[1]) for r in resources if inb(r[0], r[1]) and (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    def nearest(fromx, fromy, pool):
        best = pool[0]
        bd = abs(best[0] - fromx) + abs(best[1] - fromy)
        for rx, ry in pool[1:]:
            d = abs(rx - fromx) + abs(ry - fromy)
            if d < bd:
                bd, best = d, (rx, ry)
        return best

    my_t = nearest(sx, sy, res)
    opp_t = nearest(ox, oy, res)

    def opp_greedy_move(px, py, target):
        tx, ty = target
        best = (0, 0)
        bestd = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = px + dx, py + dy
                if not inb(nx, ny) or (nx, ny) in obs:
                    continue
                d = abs(nx - tx) + abs(ny - ty)
                if bestd is None or d < bestd or (d == bestd and (dx, dy) < best):
                    bestd, best = d, (dx, dy)
        return best

    def best_res_on_move(nx, ny):
        return 1 if (nx, ny) in set(res) else 0

    opp_dxdy = opp_greedy_move(ox, oy, opp_t)
    o_next = (ox + opp_dxdy[0], oy + opp_dxdy[1])
    o_dist_after = abs(o_next[0] - opp_t[0]) + abs(o_next[1] - opp_t[1])

    best_move = (0, 0)
    best_val = None
    resset = set(res)

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my_dist = abs(nx - my_t[0]) + abs(ny - my_t[1])
        pickup = 1 if (nx, ny) in resset else 0
        # Interception pressure: if we are closer than opponent to our own target, value increases.
        my_to_opp_t = abs(nx - opp_t[0]) + abs(ny - opp_t[1])
        opp_to_opp_t = abs(o_next[0] - opp_t[0]) + abs(o_next[1] - opp_t[1])
        inter = 1 if my_to_opp_t < opp_to_opp_t else 0
        # Favor pickups and reducing my distance; also try to keep opponent farther.
        val = (-1000 * pickup) + (my_dist * 10) + (my_to_opp_t * 2) - (o_dist_after * 3) - (inter * 50)
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]