def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles if p and len(p) == 2}
    self_terr = {(p[0], p[1]) for p in (observation.get("self_territory") or []) if p and len(p) == 2}
    opp_terr = {(p[0], p[1]) for p in (observation.get("opponent_territory") or []) if p and len(p) == 2}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or []) if p and len(p) == 2}

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    # Opponent centroid (deterministic, robust)
    if opp_terr:
        cx = sum(x for x, y in opp_terr) // len(opp_terr)
        cy = sum(y for x, y in opp_terr) // len(opp_terr)
    else:
        cx, cy = w - 1, h - 1

    def adj_to_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_terr:
                    return True
        return False

    def min_dist_to_opp(x, y):
        if not opp_terr:
            return 99
        md = 99
        for px, py in opp_terr:
            d = abs(px - x) + abs(py - y)
            if d < md:
                md = d
                if md == 0:
                    break
        return md

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-breaking: fixed order above
    best_score = -10**9
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obs:
            # Engine would keep in place; model that as staying with heavy penalty to avoid obstacles.
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Evaluate capture potential (flip on entry is enabled)
        score = 0
        if (nx, ny) in opp_terr:
            score += 7  # immediate flipping
        elif (nx, ny) in unclaimed:
            score += 4  # expanding into neutral
        elif (nx, ny) in self_terr:
            score += 2  # maintain

        # Press opponent by targeting adjacency to their territory
        if adj_to_opp(nx, ny):
            score += 3

        # Distance shaping: move closer to opponent territory if we can pressure;
        # otherwise prefer staying away from opponent if we're not making progress.
        md = min_dist_to_opp(nx, ny)
        score += (7 - md) * 0.25

        # Also prefer increasing distance from opponent centroid when we're already inside their pressure zone
        # (prevents suicidal straight lines once flipped cells block you)
        score += -0.05 * (abs(nx - cx) + abs(ny - cy))

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move