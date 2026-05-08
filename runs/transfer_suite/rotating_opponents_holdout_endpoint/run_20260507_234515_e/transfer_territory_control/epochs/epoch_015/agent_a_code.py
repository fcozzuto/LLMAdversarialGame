def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    ox, oy = int(op[0]), int(op[1])

    def to_cells(lst):
        out = []
        for p in (lst or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                out.append((int(p[0]), int(p[1])))
        return out

    obstacles = set(to_cells(observation.get("obstacles", []) or []))
    unclaimed = set(to_cells(observation.get("unclaimed_cells", []) or []))
    self_terr = set(to_cells(observation.get("self_territory", []) or []))
    opp_terr = set(to_cells(observation.get("opponent_territory", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    best = (0, 0)
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in self_terr:
            score += 3
        elif (nx, ny) in unclaimed:
            score += 8
        elif (nx, ny) in opp_terr:
            # flipping is enabled on entry; prefer only if it's closer to expanding than retreating
            score += 4

        # Prefer cells that help expand: adjacent to our territory, or adjacent to unclaimed
        adj_self = 0
        adj_unclaimed = 0
        adj_opp = 0
        for ddx, ddy in neigh:
            ax, ay = nx + ddx, ny + ddy
            if not inside(ax, ay):
                continue
            if (ax, ay) in self_terr:
                adj_self += 1
            elif (ax, ay) in unclaimed:
                adj_unclaimed += 1
            elif (ax, ay) in opp_terr:
                adj_opp += 1
        score += 2 * adj_self + 1 * adj_unclaimed - 1.5 * adj_opp

        # Avoid stepping toward opponent; but don't stall if we can grab unclaimed
        dist_opp = abs(nx - ox) + abs(ny - oy)
        score += 0.15 * dist_opp

        # Deterministic tie-break: prefer lower dx, then lower dy magnitude, then directness to nearest unclaimed
        if unclaimed:
            # approximate: compare by distance to nearest unclaimed without full search
            # (use small deterministic sample if many)
            us = list(unclaimed)
            k = 0
            if len(us) > 12:
                us = us[::max(1, len(us)//12)]
            best_un = None
            for ux, uy in us:
                d = abs(ux - nx) + abs(uy - ny)
                if best_un is None or d < best_un:
                    best_un = d
                    if best_un == 0:
                        break
            score += -0.4 * (best_un if best_un is not None else 0)

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]