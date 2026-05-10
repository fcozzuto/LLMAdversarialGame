def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer conquering frontier: unclaimed cells adjacent to our territory.
    frontier = []
    if self_terr:
        for (x, y) in unclaimed:
            if (x, y) in obstacles: 
                continue
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if (nx, ny) in self_terr:
                    frontier.append((x, y))
                    break
    targets = frontier if frontier else list(unclaimed)
    if not targets:
        targets = list(op_terr)

    opp_targets = []
    if op_terr:
        for (x, y) in self_terr or [(sx, sy)]:
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if (nx, ny) in op_terr:
                    opp_targets.append((nx, ny))
    if opp_targets:
        targets = opp_targets + targets

    next_cells = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        next_cells.append((dx, dy, nx, ny))

    best_move = (0, 0)
    best_score = -10**9
    for dx, dy, nx, ny in next_cells:
        cell_score = 0
        if (nx, ny) in unclaimed:
            cell_score += 8
        if (nx, ny) in op_terr:
            cell_score += 6
        if (nx, ny) in self_terr:
            cell_score += 2
        if (nx, ny) == (ox, oy):
            cell_score -= 2  # discourage direct collision-like behavior if it occurs

        # Move toward best target (closest).
        dmin = 10**9
        for t in targets[:12]:
            dmin = min(dmin, dist((nx, ny), t))
        cell_score += (20 - min(20, dmin))

        # Slight pressure away from staying in place unless it improves.
        cell_score += 0 if (dx, dy) != (0, 0) else -1
        if cell_score > best_score:
            best_score = cell_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]