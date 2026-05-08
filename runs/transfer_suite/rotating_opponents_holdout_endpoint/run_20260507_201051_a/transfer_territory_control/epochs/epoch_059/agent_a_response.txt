def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) // 2, (h - 1) // 2
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_score = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in selfT:
            cell_bonus = -3
        elif (nx, ny) in oppT:
            cell_bonus = 6
        elif (nx, ny) in unclaimed:
            cell_bonus = 4
        else:
            cell_bonus = 1

        dist_center = abs(nx - cx) + abs(ny - cy)
        dist_opp = abs(nx - ox) + abs(ny - oy)

        threat = 0
        if abs(nx - ox) <= 1 and abs(ny - oy) <= 1:
            threat = 3

        score = cell_bonus * 1000 - dist_center * 7 - dist_opp * 2 + threat * 50

        # Slight preference to break ties toward advancing (not staying still) unless already optimal
        if dx == 0 and dy == 0:
            score -= 5

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]