def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    res = [tuple(r) for r in resources if (r[0], r[1]) not in obstacles]
    if not res:
        return [0, 0]

    def best_target(px, py):
        # Returns target with minimal (distance, -resource) tie-break to be deterministic
        best = None
        bestk = None
        for rx, ry in res:
            d = cheb(px, py, rx, ry)
            k = (d, -ry, -rx)
            if bestk is None or k < bestk:
                bestk = k
                best = (rx, ry)
        return best

    my_t = best_target(sx, sy)
    op_t = best_target(ox, oy)

    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        # 2-ply-ish evaluation: compare how much this move improves my chances on my target
        # and worsens opponent chances on its target.
        my_new_t = my_t if my_t in res else best_target(nx, ny)
        op_new_t = op_t if op_t in res else best_target(ox, oy)

        myd_before = cheb(sx, sy, my_new_t[0], my_new_t[1])
        myd_after = cheb(nx, ny, my_new_t[0], my_new_t[1])

        opd_before = cheb(ox, oy, op_new_t[0], op_new_t[1])
        opd_after = cheb(ox, oy, op_new_t[0], op_new_t[1])  # opponent doesn't move; keep explicit

        # Primary: win-the-race margin after move; Secondary: prioritize reducing my distance.
        margin_after = opd_after - myd_after
        margin_before = opd_before - myd_before

        # Small strategic nudge: if we can also get closer to the opponent's current target, do it.
        cross = cheb(nx, ny, op_new_t[0], op_new_t[1]) - cheb(sx, sy, op_new_t[0], op_new_t[1])

        score = (margin_after, -(myd_after), -(margin_after - margin_before), cross, -dx, -dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]