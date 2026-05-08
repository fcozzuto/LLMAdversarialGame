def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position", [sx, sy]) or [sx, sy]
    ox, oy = int(op[0]), int(op[1])

    def to_set(key):
        s = set()
        for p in observation.get(key, []) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    self_terr = to_set("self_territory")
    resources = to_set("resources")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 200
        if (nx, ny) in resources:
            score += 120
        if any(((nx + ax), (ny + ay)) in self_terr for ax in (-1, 0, 1) for ay in (-1, 0, 1) if not (ax == 0 and ay == 0)):
            score += 15
        # Prefer moving away from opponent slightly, to reduce contest pressure
        score -= abs(nx - ox) + abs(ny - oy)
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]