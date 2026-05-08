def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set(observation.get("obstacles"))
    self_t = to_set(observation.get("self_territory"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    resources = to_set(observation.get("resources"))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick deterministic target: nearest unclaimed, else nearest resource, else chase opponent.
    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    elif resources:
        tx, ty = min(resources, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        tx, ty = ox, oy

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Reward occupying/expanding territory; penalize giving opponent immediate advantage.
        score = 0
        score += 5 if (nx, ny) in self_t else 0
        score += 3 if (nx, ny) in unclaimed else 0
        if (nx, ny) in resources:
            score += 4

        # Move closer to target.
        dist = abs(nx - tx) + abs(ny - ty)
        score += 10 - dist

        # Mildly avoid stepping adjacent to opponent.
        opp_adj = abs(nx - ox) + abs(ny - oy)
        score -= 2 if opp_adj <= 1 else 0

        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]