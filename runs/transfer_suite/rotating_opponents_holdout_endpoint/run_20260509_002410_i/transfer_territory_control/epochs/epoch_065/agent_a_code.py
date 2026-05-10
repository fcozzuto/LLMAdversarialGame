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

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def step_options():
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if inside(nx, ny) and (nx, ny) not in obstacles:
                    yield dx, dy, nx, ny

    resources = observation.get("resources") or []
    targets = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                targets.append((x, y))

    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    best = None
    best_score = -10**18

    for dx, dy, nx, ny in step_options():
        score = 0

        if (nx, ny) in oppT:
            score += 10000
        if selfT and (nx, ny) in unclaimed:
            score += 7000

        score -= 10 * (abs(nx - ox) + abs(ny - oy))
        score += -50 if (nx, ny) in obstacles else 0

        if unclaimed:
            d_unc = min((abs(nx - ux) + abs(ny - uy) for (ux, uy) in unclaimed), default=10**9)
            score += 2000 - 5 * d_unc

        if targets:
            d_res = min((abs(nx - tx) + abs(ny - ty) for (tx, ty) in targets), default=10**9)
            score += 3000 - 4 * d_res

        # small deterministic tie-breaker: prefer steps that reduce manhattan to opponent
        score += -0.001 * (abs((nx) - ox) + abs((ny) - oy))

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0] if (sx + 0, sy + 0) not in obstacles else [0, 0]