def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []
    self_set = set()
    opp_set = set()
    for p in self_t:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            self_set.add((int(p[0]), int(p[1])))
    for p in opp_t:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            opp_set.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed_set = set()
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            unclaimed_set.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (None, -10**9)

    neigh_dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
            dx, dy = 0, 0

        if (nx, ny) in self_set:
            base = 0.0
        elif (nx, ny) in opp_set:
            base = 5.0  # direct counterclaim / flip
        elif (nx, ny) in unclaimed_set:
            base = 2.0  # expansion into unknown
        else:
            base = 0.2  # safest fallback

        adj_self = 0
        adj_opp = 0
        for ddx, ddy in neigh_dirs:
            ax, ay = nx + ddx, ny + ddy
            if in_bounds(ax, ay) and (ax, ay) not in obs:
                if (ax, ay) in self_set:
                    adj_self += 1
                if (ax, ay) in opp_set:
                    adj_opp += 1

        # Move toward opponent when it doesn't sacrifice local expansion.
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        dist_curr = abs(sx - ox) + abs(sy - oy)

        score = base + 0.6 * adj_self + 1.0 * adj_opp
        score += 0.25 * (dist_curr - dist_to_opp)

        # Prefer not getting trapped behind obstacles: encourage staying on cells with >=1 free neighbor.
        free_nb = 0
        for ddx, ddy in neigh_dirs:
            ax, ay = nx + ddx, ny + ddy
            if in_bounds(ax, ay) and (ax, ay) not in obs:
                free_nb += 1
        score += 0.05 * free_nb

        # Tie-break deterministically: lower dx, then lower dy, then prefer diagonal toward opponent.
        if score > best[1] or (score == best[1] and (dx, dy) < best[0]):
            best = ((dx, dy), score)

    dx, dy = best[0]
    return [int(dx), int(dy)]