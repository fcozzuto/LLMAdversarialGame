def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb_dist(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # Choose target: prefer nearest resource where we are not slower than opponent; otherwise next best.
    target = None
    best = None
    for tx, ty in resources:
        myd = cheb_dist(sx, sy, tx, ty)
        opd = cheb_dist(ox, oy, tx, ty)
        # Primary: minimize my distance; Secondary: avoid giving opponent advantage; Tertiary: deterministic by coord
        key = (myd, opd - myd, tx + ty * 1000)
        if best is None or key < best:
            best = key
            target = (tx, ty)

    if target is None:
        # Safe fallback: drift toward center-ish while keeping away from opponent
        tx, ty = w // 2, h // 2
    else:
        tx, ty = target

    best_move = [0, 0]
    best_eval = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obst or not (0 <= nx < w and 0 <= ny < h):
            continue
        d_to = cheb_dist(nx, ny, tx, ty)
        d_opp = cheb_dist(nx, ny, ox, oy)
        # Encourage progress to target and slightly distance from opponent; deterministic tie-break by (dx,dy)
        eval_key = (d_to, -(d_opp), dx, dy)
        if best_eval is None or eval_key < best_eval:
            best_eval = eval_key
            best_move = [dx, dy]

    return best_move