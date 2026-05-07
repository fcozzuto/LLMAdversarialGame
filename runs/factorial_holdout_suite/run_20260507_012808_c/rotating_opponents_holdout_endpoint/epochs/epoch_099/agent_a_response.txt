def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    def xy(v):
        try:
            return int(v[0]), int(v[1])
        except:
            return 0, 0

    sx, sy = xy(observation.get("self_position"))
    ox, oy = xy(observation.get("opponent_position"))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = xy(p)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x, y = xy(r)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Evaluate candidate targets; switch to "margin-first" with obstacle-aware local escape.
    best = None
    best_key = None
    center_bias = abs(sx - (w - 1) / 2.0) + abs(sy - (h - 1) / 2.0)
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        margin = myd - opd  # negative => we are ahead (good)
        row_sync = -abs(sy - ty)  # prefer resources in our row/near row first for sweep_rows pressure
        col_sync = -abs(sx - tx)
        # deterministic obstacle-ish penalty: if target is "shielded" by obstacles nearby, avoid it
        block = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = tx + dx, ty + dy
                if (nx, ny) in obstacles:
                    block += 1
        # Earlier turns should prioritize tempo; later turns prioritize winning margin.
        tr = int(observation.get("turns_remaining") or 0)
        tempo = (tr / 100.0) if tr > 0 else 1.0
        key = (margin, block, myd, -row_sync, -col_sync, -tempo, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    # Choose the move that best decreases our distance, but avoid stepping into obstacles; deterministic tie-break.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    best_k = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        step_center = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
        # Prefer moves that keep us ahead and approach target quickly.
        k = (myd2, myd2 - opd2, step_center, dx, dy)
        if best_k is None or k < best_k:
            best_k = k
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]