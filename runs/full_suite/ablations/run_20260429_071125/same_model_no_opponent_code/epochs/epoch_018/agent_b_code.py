def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    def read_xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            if "x" in v and "y" in v:
                return int(v["x"]), int(v["y"])
            p = v.get("position", None)
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return int(p[0]), int(p[1])
        return 0, 0

    sx, sy = read_xy(observation.get("self_position", [0, 0]))
    ox, oy = read_xy(observation.get("opponent_position", [0, 0]))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        x, y = read_xy(p)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        x, y = read_xy(p)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        ax = dx if dx >= 0 else -dx
        ay = dy if dy >= 0 else -dy
        return ax if ax > ay else ay

    target = None
    if resources:
        best = None
        for tx, ty in resources:
            myd = cheb(sx, sy, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Prefer resources we can reach sooner; tie-break deterministically by coords
            key = (myd > opd, myd, tx, ty)
            if best is None or key < best[0]:
                best = (key, tx, ty)
        target = (best[1], best[2])

    # Fallback target: center (or nearest corner if center blocked)
    if target is None:
        cx, cy = w // 2, h // 2
        if (cx, cy) in obstacles:
            cx, cy = 0 if sx < w // 2 else w - 1, 0 if sy < h // 2 else h - 1
        target = (cx, cy)

    tx, ty = target

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Ensure we don't get stuck off-grid/into obstacles; choose min distance after move with deterministic tie-break
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Prefer moves that reduce our distance; also slightly prefer staying away from opponent when tied
        away = cheb(nx, ny, ox, oy)
        val = (myd2 > opd2, myd2, -away, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]