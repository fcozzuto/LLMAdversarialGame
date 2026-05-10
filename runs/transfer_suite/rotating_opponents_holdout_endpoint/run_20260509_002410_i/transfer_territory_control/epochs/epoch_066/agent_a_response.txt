def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    resources = observation.get("resources") or []
    res = None
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                res = (x, y)
                break

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    center_dist = lambda x, y: abs(x - cx) + abs(y - cy)
    dist_to_opp = lambda x, y: abs(x - ox) + abs(y - oy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None  # (score, tie, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in oppT:
            score += 1000
        elif (nx, ny) in unclaimed:
            score += 150
        elif (nx, ny) in selfT:
            score += 25
        # pressure: move toward opponent and center; if resource exists, prefer it
        dOpp = dist_to_opp(nx, ny)
        score += 40 / (1 + dOpp)
        score -= 0.1 * center_dist(nx, ny)
        if res is not None:
            rx, ry = res
            score += 10 / (1 + (abs(nx - rx) + abs(ny - ry)))
        # tie-break deterministically: prefer lower (dx,dy) order and better distances
        tie = (dOpp, abs(nx - ox) + abs(ny - oy), center_dist(nx, ny), dx, dy)
        cand = (score, tie, dx, dy)
        if best is None or cand[0] > best[0] or (cand[0] == best[0] and cand[1] < best[1]):
            best = cand

    if best is None:
        return [0, 0]
    return [int(best[2]), int(best[3])]