def choose_move(observation):
    x, y = observation.get("self_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    opp_cells = set(tuple(c) for c in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(c) for c in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(c) for c in (observation.get("obstacles") or []))

    cx, cy = w // 2, h // 2
    if opp_cells:
        sx = 0
        sy = 0
        n = len(opp_cells)
        for px, py in opp_cells:
            sx += px
            sy += py
        ocx = sx // n
        ocy = sy // n
    else:
        ocx, ocy = cx, cy

    def clamp(px, py):
        return 0 <= px < w and 0 <= py < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-10**18, 0, 0)

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not clamp(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_cells:
            cell_score = 6.0
        elif (nx, ny) in unclaimed:
            cell_score = 3.5
        else:
            cell_score = 1.0 if observation.get("self_territory") and [nx, ny] in observation.get("self_territory") else 1.0

        dist_to_opp = abs(nx - ocx) + abs(ny - ocy)
        dist_to_center = abs(nx - cx) + abs(ny - cy)

        move_score = cell_score * 10.0 + (-dist_to_opp) * 1.2 + (-dist_to_center) * 0.15
        if (dx == 0 and dy == 0):
            move_score -= 0.25

        if move_score > best[0] or (move_score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (move_score, dx, dy)

    return [int(best[1]), int(best[2])]