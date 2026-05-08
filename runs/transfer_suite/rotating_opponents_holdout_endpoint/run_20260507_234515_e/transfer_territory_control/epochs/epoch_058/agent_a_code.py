def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = w // 2, h // 2

    def tile_score(x, y):
        if (x, y) in obstacles:
            return -10**9
        score = 0
        if (x, y) in opp_terr:
            score += 25
        elif (x, y) in unclaimed:
            score += 6
        elif (x, y) in self_terr:
            score += 3
        dx1, dy1 = x - cx, y - cy
        score += -0.15 * (abs(dx1) + abs(dy1))
        do = abs(x - ox) + abs(y - oy)
        score += 0.05 * do  # slightly prefer keeping distance from opponent to avoid being boxed
        # Prefer cells that are adjacent to opponent territory (frontier pressure)
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (x + ax, y + ay) in opp_terr:
                    score += 4
        return score

    best_dx, best_dy = 0, 0
    best_val = tile_score(sx, sy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = tile_score(nx, ny)
        if val > best_val or (val == best_val and (dx, dy) < (best_dx, best_dy)):
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]