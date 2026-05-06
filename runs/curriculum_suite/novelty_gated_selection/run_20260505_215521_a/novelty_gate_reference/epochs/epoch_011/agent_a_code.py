def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    if not resources:
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            key = (d, abs(nx - sx) + abs(ny - sy), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    center_bias = cheb(sx, sy, w // 2, h // 2)
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Pick the resource that we can reach well before the opponent.
        best_move_score = None
        best_r = None
        for rx, ry in resources:
            usd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer low us distance, and large opponent distance.
            # Deterministic tie-breaking prefers closer (usd, then -opd).
            score = (usd - 0.55 * opd, usd, -opd, rx, ry)
            if best_move_score is None or score < best_move_score:
                best_move_score = score
                best_r = (rx, ry)

        rx, ry = best_r
        # Additional move evaluation:
        # - keep us not too close to opponent early (avoid giving them tempo)
        # - avoid leaving us far from that chosen resource
        opp_separation = cheb(nx, ny, ox, oy)
        goal_sep = cheb(nx, ny, rx, ry)
        d_center = cheb(nx, ny, w // 2, h // 2)
        key = (
            best_move_score[0],          # primary: advantage for the chosen resource
            goal_sep,                   # secondary: how close we are to it now
            -opp_separation,            # secondary: keep away from opponent
            d_center,                   # tertiary: mild center bias (stable)
            (nx - sx), (ny - sy)       # deterministic tie-break
        )
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]] if best else [0, 0]