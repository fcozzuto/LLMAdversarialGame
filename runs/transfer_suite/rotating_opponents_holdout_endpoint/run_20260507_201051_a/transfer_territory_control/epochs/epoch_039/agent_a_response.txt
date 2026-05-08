def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_count_to(cell_set, x, y):
        c = 0
        for ax, ay in neigh:
            if (x + ax, y + ay) in cell_set:
                c += 1
        return c

    frontier = []
    for ux, uy in unclaimed:
        for ax, ay in neigh:
            if (ux + ax, uy + ay) in self_t:
                frontier.append((ux, uy))
                break

    best_sc = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        c_un = 1 if (nx, ny) in unclaimed else 0
        c_self = 1 if (nx, ny) in self_t else 0
        c_opp = 1 if (nx, ny) in opp_t else 0

        sc = 0
        sc += c_un * 2.2
        sc += c_opp * 4.0  # flipping opponent territory on entry
        sc += adj_count_to(self_t, nx, ny) * 0.9
        sc -= adj_count_to(opp_t, nx, ny) * (0.15 if c_opp == 0 else 0.05)

        if frontier:
            md = 10**9
            for tx, ty in frontier:
                d = abs(tx - nx) + abs(ty - ny)
                if d < md:
                    md = d
            sc -= md * 0.03
        else:
            sc -= (abs(nx - (w - 1)) + abs(ny - (h - 1))) * 0.0  # deterministic no-op

        if sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]