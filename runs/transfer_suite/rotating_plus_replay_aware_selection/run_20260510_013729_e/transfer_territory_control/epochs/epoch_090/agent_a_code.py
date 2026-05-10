def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_t = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_t.add((int(p[0]), int(p[1])))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_t.add((int(p[0]), int(p[1])))

    targets = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles and (x, y) not in self_t and (x, y) not in opp_t:
                targets.append((x, y))

    if not targets:
        targets = [(x, y) for (x, y) in opp_t if (x, y) not in obstacles]
    if not targets:
        targets = [(ox, oy)]
    if not targets:
        return [0, 0]

    best = None
    best_score = None
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dmin = 10**9
        inv = 0
        for tx, ty in targets:
            d = abs(tx - nx) + abs(ty - ny)
            if d < dmin:
                dmin = d
        if (nx, ny) in opp_t:
            inv = 1
        if (nx, ny) in self_t:
            inv -= 1
        score = dmin - 2 * inv
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]