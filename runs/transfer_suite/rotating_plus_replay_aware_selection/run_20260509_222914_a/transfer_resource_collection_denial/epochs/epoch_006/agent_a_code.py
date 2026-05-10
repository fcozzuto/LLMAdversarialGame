def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None
        best_key = None
        for rx, ry in resources:
            sd = cheb(x, y, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            key = (-(adv), sd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    # Choose move that gets us closer while not stepping into obstacles; also lightly consider cutting off opponent.
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0: nx = 0
        if nx >= w: nx = w - 1
        if ny < 0: ny = 0
        if ny >= h: ny = h - 1
        if (nx, ny) in obstacles:
            continue
        my_d = cheb(nx, ny, tx, ty)
        cur_d = cheb(x, y, tx, ty)
        # Prefer reducing distance; avoid stagnation; also consider how much this worsens opponent access.
        op_d = cheb(ox, oy, tx, ty)
        nxt_op_adv = op_d - cheb(nx, ny, tx, ty)
        stagn = 1 if my_d >= cur_d else 0
        score = (0 - nxt_op_adv, my_d, stagn, nx, ny, dx, dy)  # lexicographic min
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]