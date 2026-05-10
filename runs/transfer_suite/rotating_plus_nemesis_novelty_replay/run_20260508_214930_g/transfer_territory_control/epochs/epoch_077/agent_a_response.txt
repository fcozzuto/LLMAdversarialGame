def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh8 = dirs

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def counts(x, y):
        a_my = a_opp = a_un = 0
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                if (nx, ny) in self_t:
                    a_my += 1
                elif (nx, ny) in opp_t:
                    a_opp += 1
                elif (nx, ny) in unclaimed:
                    a_un += 1
        return a_my, a_opp, a_un

    base_opp_dist = abs(sx - ox) + abs(sy - oy)
    best = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        a_my, a_opp, a_un = counts(nx, ny)
        cell_in_opp = (nx, ny) in opp_t
        cell_in_un = (nx, ny) in unclaimed
        cell_in_self = (nx, ny) in self_t

        score = 0
        if cell_in_opp:
            score += 800 + a_my * 80 - a_opp * 40 - abs((nx - ox) + (ny - oy)) * 2
        elif cell_in_un:
            score += 120 + a_my * 60 + a_un * 10
            score -= a_opp * 25
        elif cell_in_self:
            score += 40 + a_my * 20
        else:
            score += 5  # staying/stepping into rare non-territory

        nd = abs(nx - ox) + abs(ny - oy)
        score += (base_opp_dist - nd) * 3  # slight pressure toward enemy area
        score += a_my * 8  # strengthen our local hold

        # tie-break deterministically: prefer staying still less? prefer moves with smaller dx, then dy
        if score > best_score or (score == best_score and (dx, dy) < (best[0], best[1])):
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]