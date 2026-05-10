def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res_list = observation.get("resources") or []
    resources = set()
    for r in res_list:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h:
                resources.add((x, y))

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def step_options():
        opts = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    opts.append((dx, dy, nx, ny))
        opts.append((0, 0, sx, sy))
        return opts

    candidates = []
    for tx, ty in resources:
        us = md(sx, sy, tx, ty)
        op = md(ox, oy, tx, ty)
        # Prefer resources where we aren't clearly behind; break ties with our distance
        if us <= op:
            candidates.append((0, us, op, tx, ty))
        else:
            candidates.append((1, us - op, us, tx, ty))
    # Sort: best = earlier tuple
    candidates.sort()
    best = candidates[0]
    tx, ty = best[-2], best[-1]

    opts = step_options()
    best_move = (0, 0, 10**9, 10**9, 0)
    # Evaluate moves: landing on resource first, else minimize self distance to target and avoid moving into opponent-faster positions
    for dx, dy, nx, ny in opts:
        on_res = 1 if (nx, ny) in resources else 0
        ds = md(nx, ny, tx, ty)
        dop = md(nx, ny, ox, oy)
        # If opponent is closer to the resource after our move, penalize a bit (heuristic "interception")
        d_op_to_target = md(ox, oy, tx, ty)
        my_first = md(nx, ny, tx, ty) <= d_op_to_target
        key = (-on_res, 0 if my_first else 1, ds, dop)
        if key < (best_move[2], best_move[3], best_move[4] if False else best_move[4], best_move[4]):
            best_move = (dx, dy, key[2], key[3], on_res)
    return [best_move[0], best_move[1]]