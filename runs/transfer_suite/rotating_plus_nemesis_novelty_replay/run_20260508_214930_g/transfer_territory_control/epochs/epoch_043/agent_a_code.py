def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neigh(a, x, y):
        return [(x + dx, y + dy) for dx, dy in a]

    neigh8 = [d for d in dirs if d != (0, 0)]
    cand_score = -10**18
    best = (0, 0)

    opp_border = []
    for ax, ay in opp_t:
        for nx, ny in neigh8:
            tx, ty = ax + nx, ay + ny
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles and (tx, ty) not in opp_t:
                opp_border.append((tx, ty))
    opp_border_set = set(opp_border)

    unclaimed_list = list(unclaimed)
    opp_list = list(opp_t) if opp_t else [(ox, oy)]

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue

        score = 0
        if (nx, ny) in opp_t:
            score += 5000
        if (nx, ny) in unclaimed:
            score += 120
        if (nx, ny) in self_t:
            score += 8

        d_opp = abs(nx - ox) + abs(ny - oy)
        score += (-d_opp) * 2

        if unclaimed_list:
            best_du = 10**9
            for ux, uy in unclaimed_list[:20]:
                du = abs(nx - ux) + abs(ny - uy)
                if du < best_du:
                    best_du = du
            score += (40 - best_du) * 2

        if opp_border_set and (nx, ny) in opp_border_set:
            score += 250

        # avoid walking into "trap" where opponent can immediately flip next step
        trap = 0
        for ax, ay in neigh8:
            tx, ty = nx + ax, ny + ay
            if (tx, ty) in opp_t:
                trap += 1
        score -= trap * 35

        # slight preference to expand outward (toward farthest from our territory centroid)
        if self_t:
            cx = sum(p[0] for p in self_t) / len(self_t)
            cy = sum(p[1] for p in self_t) / len(self_t)
            score += (abs(nx - cx) + abs(ny - cy)) * 0.5

        # tie-break deterministically toward lexicographically smaller (ddx, ddy)
        if score > cand_score or (score == cand_score and (ddx, ddy) < best):
            cand_score = score
            best = (ddx, ddy)

    return [int(best[0]), int(best[1])]