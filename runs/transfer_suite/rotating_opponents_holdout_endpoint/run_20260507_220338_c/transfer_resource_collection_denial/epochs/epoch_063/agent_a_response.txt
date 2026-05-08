def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    resset = set((p[0], p[1]) for p in resources if len(p) >= 2)
    obst = set((p[0], p[1]) for p in obstacles if len(p) >= 2)

    if (sx, sy) in resset:
        return [0, 0]

    def absd(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def clamp_moves(dx, dy):
        return [dx, dy]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w // 2, h // 2)
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
                continue
            d = absd(nx, ny, tx, ty)
            key = (d, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return clamp_moves(best[0], best[1]) if best is not None else [0, 0]

    best_target = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obst:
            continue
        ourd = absd(sx, sy, rx, ry)
        oppd = absd(ox, oy, rx, ry)
        # Materially different from "aim solely at closest": strongly prefer resources we can arrive first.
        winprio = 0 if ourd < oppd else 1
        key = (winprio, ourd, -(oppd), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    curd = absd(sx, sy, tx, ty)

    # Local greedy step with deterministic obstacle-aware tie-breaking.
    chosen = None
    chosen_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue
        nd = absd(nx, ny, tx, ty)
        # Prefer decreases; if tied, prefer diagonal toward target; then lexicographic.
        dec = 0 if nd < curd else (1 if nd == curd else 2)
        step_bias = 0 if (dx == 0 or dy == 0) else -1
        key = (dec, nd, step_bias, dx, dy)
        if chosen_key is None or key < chosen_key:
            chosen_key = key
            chosen = (dx, dy)

    return clamp_moves(chosen[0], chosen[1]) if chosen is not None else [0, 0]