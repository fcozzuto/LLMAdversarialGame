def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    ox, oy = observation.get("opponent_position", (x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    opp_list = list(oppT)
    self_list = list(selfT)

    def min_dist_to(points, px, py):
        best = 10**9
        for a, b in points:
            d = md(px, py, a, b)
            if d < best:
                best = d
        return best if points else 10**9

    best = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue

        score = 0.0
        if (nx, ny) in oppT:
            score += 30.0
            # prefer cutting through where opponent has more neighboring territory
            neigh_opp = 0
            for ddx, ddy in dirs:
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in oppT:
                    neigh_opp += 1
            score += 3.0 * neigh_opp

        if (nx, ny) in selfT:
            score += 6.0
        elif (nx, ny) in unclaimed:
            score += 14.0
            # encourage unclaimed near our current frontier and near opponent's frontier (to preempt)
            adj_self = 0
            adj_opp = 0
            for ddx, ddy in dirs:
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if 0 <= ax < w and 0 <= ay < h:
                    if (ax, ay) in selfT:
                        adj_self += 1
                    if (ax, ay) in oppT:
                        adj_opp += 1
            score += 2.0 * adj_self + 1.5 * adj_opp

        # avoid traps: getting too close to opponent's territory unless we're stealing/advancing into it
        d_opp_from_here = min_dist_to(opp_list, nx, ny)
        d_self_from_here = min_dist_to(self_list, nx, ny)
        score += 0.4 * d_self_from_here - 0.7 * d_opp_from_here

        # if opponent is likely to reach an unclaimed spot first, don't drift away
        if unclaimed:
            d_to_opp = min(md(nx, ny, a, b) for a, b in [(u[0], u[1]) for u in unclaimed])
            score -= 0.05 * d_to_opp

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best