def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    self_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)
    def border_dist(x, y):
        return min(x, y, (w - 1) - x, (h - 1) - y)

    interior = [p for p in unclaimed if border_dist(p[0], p[1]) >= 2]
    if interior:
        targets = interior
    else:
        targets = list(unclaimed)

    # Deterministic tie-break: fixed move order and lexicographic candidate cell.
    best = None
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        score = 0
        if (nx, ny) in opp_set:
            score += 8  # flipping is strong
        elif (nx, ny) in unclaimed:
            score += 3  # secure new territory
        elif (nx, ny) in self_set:
            score += 0

        # Prefer interior growth (anti edge-claimer)
        if targets:
            best_d = 10**9
            for tx, ty in targets[:12]:
                d = manh(nx, ny, tx, ty)
                if d < best_d:
                    best_d = d
            score += max(0, 6 - best_d)  # closer to an unclaimed target is better
        score += border_dist(nx, ny) * 0.25

        # Penalize moving next to opponent unless it is an opponent flip
        adj_opp = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in opp_set:
                    adj_opp += 1
        if (nx, ny) not in opp_set:
            score -= adj_opp * 0.6

        if (score > best_score) or (score == best_score and (nx, ny) < (best[0], best[1]) if best else True):
            best_score = score
            best = (nx, ny, dx, dy)

    return [best[2], best[3]]