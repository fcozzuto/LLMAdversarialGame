def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is not None and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    if resources:
        targets = list(dict.fromkeys(resources))
    else:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        targets = [(cx, cy)]

    opp_dist = abs(sx - ox) + abs(sy - oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        mind = None
        for tx, ty in targets:
            d = abs(nx - tx) + abs(ny - ty)
            if mind is None or d < mind:
                mind = d
        if mind is None:
            mind = 0
        # Prefer closer to resource; if tie, keep some distance from opponent.
        sd = abs((nx - ox) + (ny - oy))
        score = (-(mind * 10), sd, -((nx + ny) % 3), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if best_score is not None else [0, 0]