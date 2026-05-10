def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obs_set = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells") or []))
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory") or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory") or []))
    ox, oy = observation.get("opponent_position") or (None, None)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def frontier(x, y):
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if (nx, ny) in selft:
                return 1
        return 0

    best = [0, 0]
    best_sc = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obs_set:
                continue
            sc = 0
            if (nx, ny) in opp:
                d = man(nx, ny, ox, oy) if ox is not None else 0
                sc += 420 - 3 * d
                sc += 35 * frontier(nx, ny)
            elif (nx, ny) in unclaimed:
                d_opp = man(nx, ny, ox, oy) if ox is not None else 0
                d_self = man(nx, ny, sx, sy)
                sc += 160 - d_opp - d_self * 0.5
                sc += 55 * frontier(nx, ny)
                if (nx, ny) in unclaimed and (nx, ny) != (sx, sy):
                    sc += 6
            elif (nx, ny) in selft:
                sc += 18
                sc += 25 * frontier(nx, ny)
            else:
                sc += 2
            if (nx, ny) in opp and (sx, sy) in selft:
                sc += 10
            if ox is not None:
                d_op_here = man(nx, ny, ox, oy)
                sc += -0.2 * d_op_here
            if sc > best_sc:
                best_sc = sc
                best = [dx, dy]
    return best