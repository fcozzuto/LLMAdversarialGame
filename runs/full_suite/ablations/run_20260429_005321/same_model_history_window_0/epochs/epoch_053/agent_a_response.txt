def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = cheb((sx, sy), (rx, ry))
        od = cheb((ox, oy), (rx, ry))
        # Prefer resources we can reach sooner; tie-break by farther from opponent to avoid races.
        key = (sd - od, sd, -od, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    # Candidate move: step toward target; if blocked, choose best alternative deterministically.
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = [(dx, dy)]
    # Add remaining directions in deterministic order, excluding duplicates.
    for d in dirs:
        if d not in candidates:
            candidates.append(d)

    best_move = (0, 0)
    best_score = None
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        # Score: minimize distance to target; if close, prefer move that also increases distance from opponent.
        myd = cheb((nx, ny), (tx, ty))
        oppd = cheb((ox, oy), (tx, ty))
        score = (myd, -oppd, abs(mx) + abs(my), mx, my)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]