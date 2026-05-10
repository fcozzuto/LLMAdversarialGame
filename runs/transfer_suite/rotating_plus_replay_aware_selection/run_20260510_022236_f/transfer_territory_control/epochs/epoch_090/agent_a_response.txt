def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    up = int(observation.get("self_territory_count") or 0)
    op = int(observation.get("opponent_territory_count") or 0)
    behind = up < op

    deltas = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def nearest_dist(x, y, cells, cap=24):
        if not cells:
            return 10**9
        it = 0
        best = 10**9
        for (px, py) in cells:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
            it += 1
            if it >= cap and best == 0:
                break
        return best

    # Precompute targets for short evaluation
    targets_unclaimed = list(unclaimed)
    if behind and not targets_unclaimed:
        targets_unclaimed = list(op_terr)

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine keeps in place on invalid
        cell = (nx, ny)

        score = 0.0

        # Territory flipping incentives
        if cell in op_terr:
            score += 220.0
        elif cell in unclaimed:
            score += 90.0
        elif cell in self_terr:
            score += 15.0
        else:
            score += 5.0

        # Push toward center when behind, otherwise maintain pressure on opponent area
        dist_center = abs(nx - cx) + abs(ny - cy)
        if behind:
            score += -2.2 * dist_center
        else:
            # Move to be closer to opponent territory border/near cells that are not ours
            score += -1.6 * nearest_dist(nx, ny, op_terr)

        # Prefer reducing distance to unclaimed when possible
        if targets_unclaimed:
            score += -1.2 * nearest_dist(nx, ny, targets_unclaimed)

        # Slightly discourage oscillation / staying if another move seems equally good
        if (dx, dy) == (0, 0):
            score -= 6.0

        # Deterministic tie-break: fixed order of deltas
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]