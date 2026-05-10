def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    def to_set(v):
        out = set()
        if not v:
            return out
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                out.add((int(p[0]), int(p[1])))
        return out

    obstacles = to_set(observation.get("obstacles") or [])
    unclaimed = to_set(observation.get("unclaimed_cells") or [])
    selfT = to_set(observation.get("self_territory") or [])
    oppT = to_set(observation.get("opponent_territory") or [])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    targets = list(unclaimed) if unclaimed else (list(oppT) if oppT else [])

    def best_unclaimed_dist2(x, y):
        if not targets:
            return 9999
        md = 9999
        for tx, ty in targets:
            if (tx, ty) in obstacles:
                continue
            d = (tx - x) * (tx - x) + (ty - y) * (ty - y)
            if d < md:
                md = d
        return md

    best_opp_corner_dist2 = (ox - (w - 1)) * (ox - (w - 1)) + (oy - (h - 1)) * (oy - (h - 1))

    # Deterministic tie-break order: fixed move order
    order = [(dx, dy) for (dx, dy) in neigh8]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in selfT:
            score += 1
        if (nx, ny) in unclaimed:
            score += 4
        if (nx, ny) in oppT:
            score += 7  # flipping on entry
        # Prefer expanding toward nearby unclaimed
        score -= 0.02 * best_unclaimed_dist2(nx, ny)
        # Prefer pressuring opponent when nearby
        d_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score += 0.04 * (64 - min(64, d_opp))
        # Mild preference for keeping central-ish if no targets
        if not targets:
            score += -0.001 * (nx * nx + ny * ny) + 0.0005 * best_opp_corner_dist2

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]