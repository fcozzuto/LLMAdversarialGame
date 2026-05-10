def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def adj_unclaimed(x, y):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    def adj_self(x, y):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in self_terr:
                c += 1
        return c

    def adj_opp(x, y):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in opp_terr:
                c += 1
        return c

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_score = -10**18

    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        au = adj_unclaimed(nx, ny)
        aS = adj_self(nx, ny)
        aO = adj_opp(nx, ny)

        if (nx, ny) in unclaimed:
            score += 18.0 * au + 2.0 * aS
            score -= 4.0 * aO  # avoid walking into enemy-front if it offers no growth
        elif (nx, ny) in opp_terr:
            # only take opponent territory if it also opens frontier (unclaimed adjacency)
            score += 16.0 * au + 6.0 * aS
            score += 8.0 * adj_opp(nx, ny)  # penalize less when it's contested (likely part of sweep line)
            score -= 10.0 if aO == 0 else 0.0
        elif (nx, ny) in self_terr:
            score += 3.0 * aS
            score += 1.0 * au
        else:
            # unknown/untracked cell (should be rare) treat as mild step toward center
            score += 1.0 * au + 0.5 * aS

        # center bias to prevent oscillation on flat frontiers
        dist = abs(nx - cx) + abs(ny - cy)
        score -= 0.15 * dist

        # deterministic tie-break via (dx,dy)
        key = (dx, dy)
        if score > best_score or (score == best_score and (best is None or key < best)):
            best_score = score
            best = key

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]