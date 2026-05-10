def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Frontier: unclaimed cells adjacent (8-neigh) to opponent territory
    opp_frontier = set()
    for (ux, uy) in unclaimed:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (ux + dx, uy + dy) in opp_terr:
                    opp_frontier.add((ux, uy))
                    break
            else:
                continue
            break

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Precompute nearest distances sets for evaluation
    un_list = list(unclaimed)
    frontier_list = list(opp_frontier)
    opp_list = list(opp_terr)

    def nearest_dist(cell, targets):
        if not targets:
            return 999
        best = 999
        for t in targets:
            d = cheb(cell, t)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    best_val = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -10**12
        else:
            cell = (nx, ny)
            val = 0.0
            if cell in self_terr:
                val += 0.1
            elif cell in unclaimed:
                val += 6.0
            elif cell in opp_terr:
                val += 9.0
            else:
                val += 1.0

            d_un = nearest_dist((nx, ny), un_list)
            d_front = nearest_dist((nx, ny), frontier_list)
            d_opp = nearest_dist((nx, ny), opp_list)

            # Greedy progress to secure territory and to cut opponent via frontier
            val += (-0.35 * d_un) + (-0.55 * d_front) + (-0.12 * d_opp)

            # Small bias: prefer reducing distance to opponent when no frontier/unclaimed exist
            if not frontier_list and not un_list:
                val += (-0.3 * cheb((nx, ny), observation.get("opponent_position") or [w - 1, h - 1]))

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]