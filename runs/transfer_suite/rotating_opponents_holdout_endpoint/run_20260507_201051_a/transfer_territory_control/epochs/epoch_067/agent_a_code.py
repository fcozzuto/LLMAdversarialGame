def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    opp_cells = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_cells.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    opp_cent = None
    if opp_cells:
        ax = ay = 0
        for x, y in opp_cells:
            ax += x
            ay += y
        opp_cent = (ax // len(opp_cells), ay // len(opp_cells))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # nearest unclaimed for shaping
    nearest_uc = None
    bestd = 10**9
    for x, y in unclaimed:
        d = abs(x - sx) + abs(y - sy)
        if d < bestd:
            bestd = d
            nearest_uc = (x, y)
    target = nearest_uc

    def dist_to_center(x, y):
        dx = x - cx
        dy = y - cy
        return dx * dx + dy * dy

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        if (nx, ny) in opp_cells:
            # immediate counterclaim
            score = 2000.0
            if opp_cent:
                score += -0.5 * (abs(nx - opp_cent[0]) + abs(ny - opp_cent[1]))
            else:
                score += -0.1 * dist_to_center(nx, ny)
        elif (nx, ny) in (unclaimed and set(unclaimed) or set()):
            # claim frontier towards unclaimed
            score = 50.0
            if target:
                score += -1.0 * (abs(target[0] - nx) + abs(target[1] - ny))
            score += -0.01 * dist_to_center(nx, ny)
        else:
            # avoid wandering too much; prefer staying near center if no targets
            if target is None:
                score = -0.5 * dist_to_center(nx, ny)
            else:
                score = -0.3 * (abs(target[0] - nx) + abs(target[1] - ny))
                score += -0.01 * dist_to_center(nx, ny)

        # deterministic tie-breaker: higher score, then smaller dx, then smaller dy
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]