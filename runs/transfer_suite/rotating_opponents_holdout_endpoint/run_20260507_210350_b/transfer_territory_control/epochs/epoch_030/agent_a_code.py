def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or (sx, sy)
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                self_terr.add((x, y))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_terr.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        cell_score = 0
        if (nx, ny) in self_terr:
            cell_score += 1.0
        elif (nx, ny) in unclaimed:
            cell_score += 2.5
        elif (nx, ny) in opp_terr:
            cell_score += 6.0
        else:
            cell_score += 1.2

        dist_center = abs(nx - cx) + abs(ny - cy)
        dist_op = abs(nx - ox) + abs(ny - oy)
        score = cell_score + (8.0 - dist_center) * 0.45 + dist_op * 0.05

        if best is None or score > best[0]:
            best = (score, dx, dy)
        elif score == best[0]:
            if (dx, dy) < (best[1], best[2]):
                best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]