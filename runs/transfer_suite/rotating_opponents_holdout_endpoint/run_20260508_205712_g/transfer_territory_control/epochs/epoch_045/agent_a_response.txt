def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh_unclaimed_count(x, y):
        c = 0
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            score = -10**12
        else:
            if (nx, ny) in opp_terr:
                score = -120
                score += 10 * neigh_unclaimed_count(nx, ny)  # only flip if it opens many unclaimed
                score += -1.0 * (abs(nx - ox) + abs(ny - oy))
            else:
                score = 0
                if (nx, ny) in self_terr:
                    score += 3
                if (nx, ny) in unclaimed:
                    score += 25
                    score += 6 * neigh_unclaimed_count(nx, ny)
                # prefer progressing toward center while maintaining distance from opponent slightly
                score += -0.9 * (abs(nx - cx) + abs(ny - cy))
                score += 0.6 * (abs(nx - ox) + abs(ny - oy))
            # small tie-breaker: deterministic preference for moves that reduce distance to best immediate unclaimed target
            if unclaimed:
                best_u = None
                best_d = 10**9
                for ux, uy in unclaimed:
                    d = abs(ux - nx) + abs(uy - ny)
                    if d < best_d:
                        best_d, best_u = d, (ux, uy)
                if best_u is not None:
                    score += -0.01 * best_d
        if score > best_score:
            best_score = score
            best = [dx, dy]
    return best