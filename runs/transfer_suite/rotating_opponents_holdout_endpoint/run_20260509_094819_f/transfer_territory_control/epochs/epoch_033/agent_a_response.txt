def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    myc = int(observation.get("self_territory_count", len(selfT)))
    oppc = int(observation.get("opponent_territory_count", len(oppT)))
    behind = 1 if myc < oppc else 0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def nearest_dist2(x, y, S):
        if not S:
            return 10**9
        best = 10**9
        for (tx, ty) in S:
            d = manh2(x, y, tx, ty)
            if d < best:
                best = d
        return best

    # When behind, prefer breaking into opponent territory; when ahead, expand unclaimed.
    want_unclaimed = 1 - behind
    want_opp = behind

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in selfT:
            score += 1
        elif (nx, ny) in oppT:
            score += 10 if want_opp else 2
        elif (nx, ny) in unclaimed:
            score += 7 if want_unclaimed else 4
        else:
            score += 0

        # Distance pressure toward desired targets; also slightly away from opponent when ahead.
        d_un = nearest_dist2(nx, ny, unclaimed)
        d_opp = nearest_dist2(nx, ny, oppT)
        score += (0.45 * (-(d_un if want_unclaimed else d_opp)))
        score += (0.20 * (-(d_opp if want_opp else d_un)))

        # Avoid hovering near obstacles: discourage moves adjacent to many obstacles.
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if inb(xx, yy) and (xx, yy) in obstacles:
                    adj_obs += 1
        score -= 0.6 * adj_obs

        if score > best_score or (score == best_score and [dx, dy] == best_move):
            best_score = score
            best_move = [dx, dy]

    return best_move