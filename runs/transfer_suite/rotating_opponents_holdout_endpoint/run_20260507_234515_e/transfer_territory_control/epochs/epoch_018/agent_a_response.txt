def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    opp_terr_list = observation.get("opponent_territory") or []
    opp_terr = set((int(p[0]), int(p[1])) for p in opp_terr_list)

    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    best_move = (0, 0)
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        v = 0
        if (nx, ny) in unclaimed:
            v += 50
        if (nx, ny) in opp_terr:
            v += 120  # flipping opponent territory on entry is valuable

        # adjacency pressure for claim expansion
        adj_un = 0
        adj_opp = 0
        adj_obs = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                ax, ay = nx + adx, ny + ady
                if not inside(ax, ay):
                    continue
                if (ax, ay) in obstacles:
                    adj_obs += 1
                elif (ax, ay) in unclaimed:
                    adj_un += 1
                if (ax, ay) in opp_terr:
                    adj_opp += 1

        v += 8 * adj_un
        v += 6 * adj_opp
        v -= 7 * adj_obs

        # deterministic central bias (helps vs territory_center_claim)
        v += 10 * (16 - manhattan(nx, ny, cx, cy))

        # mild momentum: avoid oscillation into danger, prefer moves that don't step next to obstacles
        v -= 2 * manhattan(nx, ny, sx, sy) * (adj_obs > 0)

        if v > bestv or (v == bestv and (dx, dy) < best_move):
            bestv = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]