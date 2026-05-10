def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def neigh_moves():
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    yield 0, 0
                else:
                    yield dx, dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    # Aim: steal near opponent and extend into frontier
    def opp_center():
        if not opp_terr:
            return ox, oy
        sxm = sum(p[0] for p in opp_terr) / len(opp_terr)
        sym = sum(p[1] for p in opp_terr) / len(opp_terr)
        return int(round(sxm)), int(round(sym))

    ocx, ocy = opp_center()

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        # Base: approach opponent centroid and midline
        d_opp = abs(nx - ocx) + abs(ny - ocy)
        d_mid = abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)
        score = -2.0 * d_opp - 0.15 * d_mid

        if (nx, ny) in opp_terr:
            score += 60  # entering opponent-owned flips control
        elif (nx, ny) in unclaimed:
            score += 25
        elif (nx, ny) in self_terr:
            score += 5  # keep momentum; lower than stealing/unclaimed

        # Prefer frontier adjacency: cells next to self to expand without overcommitting
        adj_self = 0
        adj_opp = 0
        adj_un = 0
        for mx in (-1, 0, 1):
            for my in (-1, 0, 1):
                if mx == 0 and my == 0:
                    continue
                ax, ay = nx + mx, ny + my
                if not inside(ax, ay) or (ax, ay) in obstacles:
                    continue
                if (ax, ay) in self_terr:
                    adj_self += 1
                if (ax, ay) in opp_terr:
                    adj_opp += 1
                if (ax, ay) in unclaimed:
                    adj_un += 1
        score += 2.0 * adj_self + 3.0 * adj_un + 6.0 * adj_opp

        # Reduce chance of bouncing: discourage staying unless no good option
        if dx == 0 and dy == 0:
            score -= 8

        # Deterministic tie-break
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]