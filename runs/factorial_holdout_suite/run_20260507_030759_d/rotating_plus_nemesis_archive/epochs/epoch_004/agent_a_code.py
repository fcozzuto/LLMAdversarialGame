def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        axd = dx if dx >= 0 else -dx
        ayd = dy if dy >= 0 else -dy
        return axd if axd > ayd else ayd

    # Pick resource that we can reach sooner than opponent (with strong denial pressure)
    best_res = resources[0]
    best_key = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Key: prioritize smaller advantage (myd - opd), then smaller myd, then deterministic position ordering
        key = (myd - opd, myd, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (tx, ty)

    tx, ty = best_res

    best_move = (0, 0)
    best_eval = None
    # Deterministic iteration order
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue

            my_after = cheb(nx, ny, tx, ty)
            opp_to_target = cheb(ox, oy, tx, ty)
            myd = my_after
            opd_after = cheb(nx, ny, ox, oy)  # distance to opponent (for pushing/denial style)

            # Evaluation:
            # 1) minimize my distance to target (collect sooner)
            # 2) maximize margin vs opponent reaching target (via difference my - opp_to_target)
            # 3) prefer moving farther from opponent to avoid being contested
            # 4) tie-break deterministically
            eval_key = (myd - opp_to_target, myd, -opd_after, nx, ny, dx, dy)
            if best_eval is None or eval_key < best_eval:
                best_eval = eval_key
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]