def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    oppx, oppy = observation["opponent_position"]

    def neighbors(nx, ny):
        out = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                tx, ty = nx + dx, ny + dy
                if inb(tx, ty):
                    out.append((tx, ty))
        return out

    best = deltas[4]
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        if (nx, ny) in unclaimed:
            score += 9.0
        elif (nx, ny) in oppT:
            score += 6.0
        elif (nx, ny) in selfT:
            score += 1.0
        else:
            score += 0.1

        ns = neighbors(nx, ny)
        # Expand into and around unclaimed
        score += 1.8 * sum(1 for p in ns if p in unclaimed)
        # Threaten opponent territory edges
        score += 1.2 * sum(1 for p in ns if p in oppT)
        # Avoid wandering off our claimed area too much
        score -= 0.25 if len(ns) == 0 else 0.0
        score -= 0.2 * sum(1 for p in ns if p in selfT and (nx, ny) not in selfT)
        # Centering bias (deterministic growth)
        dist_center = abs(nx - cx) + abs(ny - cy)
        score -= 0.03 * dist_center
        # Keep away from opponent directly unless capturing
        dist_opp = abs(nx - oppx) + abs(ny - oppy)
        if (nx, ny) not in oppT:
            score -= 0.05 * dist_opp
        # Small step penalty to reduce oscillation
        if dx == 0 and dy == 0:
            score -= 0.2

        if score > best_score or (score == best_score and (dx, dy) == best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]