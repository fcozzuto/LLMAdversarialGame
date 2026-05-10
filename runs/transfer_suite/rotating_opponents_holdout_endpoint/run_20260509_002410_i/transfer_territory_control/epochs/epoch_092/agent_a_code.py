def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    w = int(w); h = int(h)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    sp2 = (sx, sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    opp = observation.get("opponent_position") or sp2
    ox, oy = int(opp[0]), int(opp[1])

    targets = []
    for key in ("unclaimed_cells", "resources"):
        arr = observation.get(key) or []
        for p in arr:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    targets.append((x, y))
        if targets:
            break

    if not targets:
        targets = [(w // 2, h // 2)]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = [0, 0]

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Deterministic tie-break: smaller lexicographic dx,dy
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_t = min(manhattan(nx, ny, tx, ty) for tx, ty in targets) if targets else 10**9
        d_o = manhattan(nx, ny, ox, oy)
        # Prefer closer to target, and farther from opponent
        score = (0 - d_t) * 1000 + d_o
        key = (score, -d_t, -d_o, dx, dy)
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return best_move