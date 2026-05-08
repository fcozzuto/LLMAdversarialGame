def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    opp = observation.get("opponent_position", None)
    if opp and len(opp) >= 2:
        ox, oy = int(opp[0]), int(opp[1])
    else:
        ox, oy = sx, sy

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_step(targets, prefer_away_from_opp=False):
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if not in_bounds(nx, ny):
                    continue
                if not targets:
                    score = 0
                else:
                    score = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
                if prefer_away_from_opp:
                    score += -2 * (abs(nx - ox) + abs(ny - oy))
                else:
                    score += 2 * (abs(nx - ox) + abs(ny - oy)) * 0
                tup = (score, dx, dy)
                if best is None or tup < best:
                    best = tup
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    if resources:
        return best_step(resources, prefer_away_from_opp=False)

    cx, cy = w // 2, h // 2
    return best_step([(cx, cy)], prefer_away_from_opp=False)