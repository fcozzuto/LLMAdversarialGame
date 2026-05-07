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

    best_res = resources[0]
    best_key = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        key = (myd - opd, myd, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (tx, ty)

    tx, ty = best_res
    best_move = (0, 0)
    best_eval = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            my_after = cheb(nx, ny, tx, ty)
            opp_after = cheb(ox, oy, tx, ty)  # opponent position static this turn
            dist_to_opp_target = cheb(nx, ny, ox, oy)

            # Prefer collecting sooner (my_after), while pushing away from opponent and not helping them.
            eval_key = (my_after, -(opp_after), dist_to_opp_target, tx, ty, dx, dy)
            if best_eval is None or eval_key < best_eval:
                best_eval = eval_key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]