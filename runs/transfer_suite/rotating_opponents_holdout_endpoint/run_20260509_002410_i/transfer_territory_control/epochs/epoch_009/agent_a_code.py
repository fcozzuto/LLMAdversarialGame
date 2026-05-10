def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    if not (self_t or opp_t or unclaimed):
        return [0, 0]

    opp_list = list(opp_t) if opp_t else [(ox, oy)]
    def min_dist_to_opp(x, y):
        md = 10**9
        for px, py in opp_list:
            d = abs(x - px) + abs(y - py)
            if d < md:
                md = d
        return md

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_sc = -10**18

    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        sc = 0
        if (nx, ny) in opp_t:
            sc += 12
        elif (nx, ny) in unclaimed:
            sc += 7
        elif (nx, ny) in self_t:
            sc += 2
        else:
            sc += 1

        d_opp = abs(nx - ox) + abs(ny - oy)
        d_to_opp_territory = min_dist_to_opp(nx, ny)
        sc += (7 - d_opp) * 0.8
        sc += (7 - d_to_opp_territory) * 0.6

        if unclaimed:
            md_un = 10**9
            for ux, uy in unclaimed:
                d = abs(nx - ux) + abs(ny - uy)
                if d < md_un:
                    md_un = d
            sc += max(0, 6 - md_un) * 1.1
        else:
            sc += 1

        if sc > best_sc or (sc == best_sc and (dx, dy) == (0, 0)):
            best_sc = sc
            best = [dx, dy]

    return best if best is not None else [0, 0]