def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if not w or not h:
        return [0, 0]
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_ter = set(map(tuple, observation.get("self_territory", [])))
    opp_ter = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def adj_cnt(nx, ny, s):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in s:
                    c += 1
        return c

    def obstacle_risk(nx, ny):
        # Lower is safer; penalize being surrounded by obstacles.
        r = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in obstacles:
                    r += 1
        return r

    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        adj_self = adj_cnt(nx, ny, self_ter)
        adj_opp = adj_cnt(nx, ny, opp_ter)
        adj_unc = adj_cnt(nx, ny, unclaimed)

        # If stepping into opponent territory, favor it (flip on entry enabled).
        step_into_opp = 1 if (nx, ny) in opp_ter else 0

        # Prefer outward frontier growth; penalize adjacency to opponent unless we can flip.
        score = 0
        score += adj_self * 5
        score += adj_unc * 2
        score -= adj_opp * 3
        score += step_into_opp * 18

        # Edge pressure: approach closest point of opponent territory if we're not already strongly expanding.
        if observation.get("opponent_territory_count", 0) > 0:
            # Deterministic approximate distance: compare to nearest of a few corners of opponent territory set
            # to avoid heavy computation. Use min over at most 10 elements.
            pts = list(opp_ter)
            if len(pts) > 10:
                pts = pts[:10]
            mind = None
            for px, py in pts:
                d = abs(nx - px) + abs(ny - py)
                if mind is None or d < mind:
                    mind = d
            if mind is not None:
                score += max(0, 18 - mind) * (1 if (nx, ny) in unclaimed else 0) + (2 if step_into_opp else 0)

        # Safety: avoid obstacle-dense areas.
        score -= obstacle_risk(nx, ny) * 1.5

        # Tie-break: prefer moves that reduce distance to opponent when flipping is unlikely.
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            curd = abs(nx - ox) + abs(ny - oy)
            bestnx = x + best_move[0]
            bestny = y + best_move[1]
            bestd = abs(bestnx - ox) + abs(bestny - oy)
            if curd < bestd:
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]