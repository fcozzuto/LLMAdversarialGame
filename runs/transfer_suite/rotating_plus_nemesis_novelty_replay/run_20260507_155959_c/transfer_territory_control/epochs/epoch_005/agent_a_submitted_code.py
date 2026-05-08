def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    unclaimed = observation.get("unclaimed_cells", []) or []
    oppT = set()
    for p in (observation.get("opponent_territory", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oppT.add((p[0], p[1]))

    selfT = set()
    for p in (observation.get("self_territory", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            selfT.add((p[0], p[1]))

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    behind = observation.get("self_territory_count", 0) <= observation.get("opponent_territory_count", 0)

    best_targets = []
    if unclaimed:
        best = None
        bestd = None
        for x, y in unclaimed:
            if not inb(x, y) or (x, y) in obstacles:
                continue
            d = md(sx, sy, x, y)
            if bestd is None or d < bestd or (d == bestd and (x, y) < best):
                bestd = d
                best = (x, y)
        if best is not None:
            best_targets = [best]
    if not best_targets and oppT:
        best = None
        bestd = None
        for x, y in oppT:
            if not inb(x, y) or (x, y) in obstacles:
                continue
            d = md(sx, sy, x, y)
            if bestd is None or d < bestd or (d == bestd and (x, y) < best):
                bestd = d
                best = (x, y)
        if best is not None:
            best_targets = [best]
    if not best_targets:
        best_targets = [(ox, oy)]

    tx, ty = best_targets[0]
    if behind and unclaimed:
        # small defensive bias toward staying away from edges if losing
        if (sx == 0 or sx == w - 1 or sy == 0 or sy == h - 1):
            # pick a target that reduces edge distance if possible
            edge_best = None
            edge_bestv = None
            for x, y in unclaimed:
                if inb(x, y) and (x, y) not in obstacles:
                    v = min(x, y, w - 1 - x, h - 1 - y)
                    if edge_bestv is None or v > edge_bestv or (v == edge_bestv and (x, y) < edge_best):
                        edge_bestv = v
                        edge_best = (x, y)
            if edge_best is not None:
                tx, ty = edge_best

    best_move = (0, 0)
    best_score = None
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # prefer staying toward target, discourage moving away, and slightly avoid leaving self territory if possible
        dist_to_t = md(nx, ny, tx, ty)
        dist_from_t = md(sx, sy, tx, ty)
        score = (dist_from_t - dist_to_t) * 10 - dist_to_t
        if (nx, ny) in selfT:
            score += 3
        if behind:
            # when behind, value safety near existing territory a bit more
            if (nx, ny) in selfT:
                score += 2
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score