def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not unclaimed:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    ux_list = list(unclaimed)
    cx = sum(x for x, _ in ux_list) / len(ux_list)
    cy = sum(y for _, y in ux_list) / len(ux_list)

    def min_manhattan_to_unclaimed(x, y):
        best = 10**9
        for cx2, cy2 in ux_list:
            d = abs(cx2 - x) + abs(cy2 - y)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    def edge_adj_to_self_or_unclaimed(x, y):
        for dx, dy in dirs[:8]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in opp_t:
                return -3  # discourage being adjacent to opponent unless we capture
            if (nx, ny) in unclaimed:
                return 2   # prefer expanding towards frontiers
            if (nx, ny) in self_t:
                return 1   # keep connected expansion
        return 0

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 1200
        if (nx, ny) in opp_t:
            score += 350  # flipping into opponent territory
            score -= 20 * min_manhattan_to_unclaimed(nx, ny)

        score -= 3.0 * min_manhattan_to_unclaimed(nx, ny)
        score += 4.0 * (-(abs(nx - cx) + abs(ny - cy)))  # move toward unclaimed centroid
        score += edge_adj_to_self_or_unclaimed(nx, ny)

        if (nx, ny) == (sx, sy):
            score -= 5

        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = score

    return [int(best[0]), int(best[1])]