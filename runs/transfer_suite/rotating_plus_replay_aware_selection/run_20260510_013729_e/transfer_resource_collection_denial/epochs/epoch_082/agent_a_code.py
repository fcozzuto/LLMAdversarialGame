def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in obstacles}
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def legal(x, y):
        return inb(x, y) and (x, y) not in obst

    if not resources:
        return [0, 0]

    def best_target(ax, ay, prefer="nearest"):
        best = None
        for rx, ry in resources:
            d = man(ax, ay, rx, ry)
            if prefer == "nearest":
                key = (d, rx, ry)
            else:
                key = (d, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry, d)
        return best[1], best[2], best[3]

    tx, ty, _ = best_target(sx, sy, "nearest")

    # Choose a target we are likely to secure first: maximize opp_d - self_d, then minimize self_d.
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd
        t = (-(adv), sd, rx, ry)
        if best is None or t < best[0]:
            best = (t, rx, ry, sd, od)
    tx, ty, self_d, opp_d = best[1], best[2], best[3], best[4]

    # Predict opponent's greedy target and next step.
    op_txs, op_tys, _ = best_target(ox, oy, "nearest")

    def step_toward(ax, ay, tx2, ty2):
        best_move = (0, 0, 10**9, ax, ay)
        for mdx, mdy in moves:
            nx, ny = ax + mdx, ay + mdy
            if not legal(nx, ny):
                continue
            d = man(nx, ny, tx2, ty2)
            # Tie-break deterministically toward smaller (nx,ny)
            cand = (mdx, mdy, d, nx, ny)
            if d < best_move[2] or (d == best_move[2] and (nx, ny) < (best_move[3], best_move[4])):
                best_move = cand
        return best_move[0], best_move[1], best_move[3], best_move[4]

    odx, ody, nox, noy = step_toward(ox, oy, op_txs, op_tys)
    # Evaluate our candidate moves using predicted opponent position.
    best_score = None
    best_move = [0, 0]
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not legal(nx, ny):
            continue
        nd_self = man(nx, ny, tx, ty)
        nd_opp = man(nox, noy, tx, ty)
        # Higher is better: prefer being closer, also prefer denying opponent.
        score = (-(nd_self), (nd_opp - nd_self), -abs(mdx) - abs(mdy), nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [mdx, mdy]

    return best_move