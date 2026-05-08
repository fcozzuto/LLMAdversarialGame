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

    ox, oy = observation.get("opponent_position") or (sx, sy)
    ox, oy = int(ox), int(oy)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dist_center = abs(sx - cx) + abs(sy - cy)
    turn = int(observation.get("turn_index") or 0)
    aggressive = 1 if (turn % 2 == 0 or dist_center < (w + h) / 3.2) else 0

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)

        score = 0.0
        if cell in unclaimed:
            score += 5.0
            score += 0.5 * (1.0 / (1.0 + abs(nx - ox) + abs(ny - oy)))
        elif cell in opp_terr:
            score += 8.0 if aggressive else 7.0
            score += 0.2 * (1.0 / (1.0 + abs(nx - ox) + abs(ny - oy)))
        elif cell in self_terr:
            score += 1.0
        else:
            score -= 1.0

        score += 0.8 * (-((abs(nx - cx) + abs(ny - cy)) - dist_center))
        score += 0.1 * (-(abs(nx - ox) + abs(ny - oy)))

        if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))

    if best is None:
        return [0, 0]
    dx, dy = best[1]
    return [int(dx), int(dy)]