def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) // 2, (h - 1) // 2

    def manhattan(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    best = (0, 0)
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        v = 0
        if (nx, ny) in unclaimed:
            v += 70
        if (nx, ny) in opp_terr:
            v += 140

        # local expansion / safety
        adj_un = 0
        adj_opp = 0
        adj_obs = 0
        adj_un_gain = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if not inside(tx, ty):
                    continue
                if (tx, ty) in obstacles:
                    adj_obs += 1
                if (tx, ty) in unclaimed:
                    adj_un += 1
                if (tx, ty) in opp_terr:
                    adj_opp += 1
                if (tx, ty) in unclaimed and (tx, ty) not in opp_terr:
                    adj_un_gain += 1

        v += 6 * adj_un + 18 * adj_opp - 5 * adj_obs
        v += -0.8 * manhattan(nx, ny, cx, cy)  # drift toward center for larger territory

        # avoid getting boxed: staying still is slightly worse unless surrounded by walls/obstacles
        if dx == 0 and dy == 0:
            v -= 2 + 2 * adj_obs

        # tie-break deterministically: prefer moves in fixed order by lexicographic (dx,dy)
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]