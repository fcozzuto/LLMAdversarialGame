def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    targets = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                targets.append((x, y))
    if not targets:
        for p in observation.get("resources") or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inside(x, y):
                    targets.append((x, y))

    if not targets:
        targets = [(ox, oy)]

    # deterministic tie-breaking order
    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best = None
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        tx, ty = None, None
        md = 10**9
        for (x, y) in targets:
            d = abs(nx - x) + abs(ny - y)
            if d < md:
                md = d
                tx, ty = x, y
        # Prefer closer to target; slight bias toward opponent to score against them
        score = md * 10 + (abs(nx - ox) + abs(ny - oy))
        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]