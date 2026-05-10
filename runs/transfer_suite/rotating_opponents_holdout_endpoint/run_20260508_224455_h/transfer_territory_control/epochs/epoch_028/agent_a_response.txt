def choose_move(observation):
    w = int(observation.get("grid_width", 8)) or 8
    h = int(observation.get("grid_height", 8)) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    self_ter = set(map(tuple, observation.get("self_territory", []) or []))
    opp_ter = set(map(tuple, observation.get("opponent_territory", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))

    center = ((w - 1) / 2.0, (h - 1) / 2.0)

    opp_list = list(opp_ter) if opp_ter else []
    if opp_list:
        nearest_opp_dist = min(abs(px - sx) + abs(py - sy) for px, py in opp_list)
    else:
        nearest_opp_dist = 99

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Base value by cell ownership
        if (nx, ny) in self_ter:
            cell_val = 1.0
        elif (nx, ny) in opp_ter:
            cell_val = 6.0  # entering opponent cell flips to us (advantage)
        elif (nx, ny) in unclaimed:
            cell_val = 3.5
        else:
            cell_val = 2.0

        # Encourage progress toward center and toward opponent
        dc = abs(nx - center[0]) + abs(ny - center[1])
        do = abs(nx - ox) + abs(ny - oy)

        # If we can reduce distance to opponent territory, prefer it
        if opp_list:
            nearest_after = min(abs(px - nx) + abs(py - ny) for px, py in opp_list)
            opp_progress = (nearest_opp_dist - nearest_after)
        else:
            opp_progress = 0

        # Small preference to avoid getting stuck behind obstacles (prefer moves with more free neighbors)
        free_neighbors = 0
        for ddx, ddy in dirs:
            if ddx == 0 and ddy == 0:
                continue
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty) and (tx, ty) not in obstacles:
                free_neighbors += 1

        score = (cell_val * 10.0) + (opp_progress * 4.0) + (-dc * 0.35) + (-do * 0.08) + (free_neighbors * 0.05)

        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]