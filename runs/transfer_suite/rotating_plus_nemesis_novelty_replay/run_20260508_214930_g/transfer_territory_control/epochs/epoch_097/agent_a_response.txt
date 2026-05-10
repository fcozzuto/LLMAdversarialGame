def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_reach = lambda x, y: max(abs(x - ox), abs(y - oy)) <= 1

    best = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        score = 0
        if (nx, ny) in opp_t:
            score += 320
        elif (nx, ny) in unclaimed:
            score += 70
        if (nx, ny) in self_t:
            score += 15

        self_adj = 0
        opp_adj = 0
        un_adj = 0
        for ddx, ddy in neigh:
            ax, ay = nx + ddx, ny + ddy
            if not ok(ax, ay):
                continue
            if (ax, ay) in self_t:
                self_adj += 1
            elif (ax, ay) in opp_t:
                opp_adj += 1
            elif (ax, ay) in unclaimed:
                un_adj += 1

        score += 10 * self_adj
        score += 4 * un_adj
        score -= 8 * opp_adj

        if (nx, ny) in self_t and opp_reach(nx, ny):
            score -= 55

        score += 1.5 * (abs(nx - ox) + abs(ny - oy) < abs(sx - ox) + abs(sy - oy))

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]