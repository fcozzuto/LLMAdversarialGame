def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    if not w or not h:
        return [0, 0]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    targets = []
    for key in ("unclaimed_cells", "resources"):
        for p in (observation.get(key) or []):
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inside(x, y):
                    targets.append((x, y))
        if targets:
            break

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    corner = corners[min(range(4), key=lambda i: abs(corners[i][0] - ox) + abs(corners[i][1] - oy))]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dist_opp = abs(nx - ox) + abs(ny - oy)
        if targets:
            dist_t = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
        else:
            dist_t = abs(nx - corner[0]) + abs(ny - corner[1])
        score = (dist_opp * 3) - dist_t
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]