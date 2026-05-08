def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # deterministic fallback: drift toward center
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_delta = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # choose move maximizing guaranteed advantage over all current resources (minimax on our target selection)
        worst = None
        for tx, ty in resources:
            ds = md(nx, ny, tx, ty)
            do = md(ox, oy, tx, ty)
            # higher is better
            s = (do - ds, -ds, -(tx + ty), -md(tx, ty, w - 1, h - 1), tx, ty)
            if worst is None or s < worst:
                worst = s
        # primary: maximize our worst-case advantage; secondary: minimize our distance to best cells
        if best_score is None or worst > best_score:
            best_score = worst
            best_delta = [dx, dy]

    return [int(best_delta[0]), int(best_delta[1])]