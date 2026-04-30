def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target(myx, myy, oppx, oppy):
        if not resources:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            return (cx, cy), 0
        best = None
        for rx, ry in resources:
            myd = cheb(myx, myy, rx, ry)
            opd = cheb(oppx, oppy, rx, ry)
            # Prefer resources where we are closer; tie-break toward fewer remaining "distance to win".
            val = (opd - myd, -myd, -cheb(oppx, oppy, rx, ry), rx, ry)
            if best is None or val > best[0]:
                best = (val, (rx, ry))
        return best[1], best[0][0]

    def safe_neighbors(x, y):
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in occ:
                yield dx, dy, nx, ny
        yield 0, 0, x, y

    cx, cy = (w - 1) // 2, (h - 1) // 2
    target, _ = best_target(sx, sy, ox, oy)

    best_move = (0, 0)
    best_score = None
    for dx1, dy1, x1, y1 in safe_neighbors(sx, sy):
        # Lookahead: after this move, re-evaluate target and block by pushing away from opponent on that target.
        t2, _ = best_target(x1, y1, ox, oy)
        my_d1 = cheb(x1, y1, t2[0], t2[1])
        opp_d1 = cheb(ox, oy, t2[0], t2[1])

        # Predict opponent greedily toward that target for one step.
        opp_best = None
        for odx, ody, ox1, oy1 in safe_neighbors(ox, oy):
            v = cheb(ox1, oy1, t2[0], t2[1])
            if opp_best is None or v < opp_best[0]:
                opp_best = (v, odx, ody, ox1, oy1)

        # Score: win race (distance advantage), reduce own distance, also penalize getting closer to opponent's predicted position.
        opp_next_d = opp_best[0]
        score = (
            (opp_d1 - my_d1),                      # race advantage
            -(my_d1),                             # closer to target
            -(opp_next_d),                        # opponent not getting too good next
            -cheb(x1, y1, cx, cy) * 0.02,         # mild center bias when ties
            cheb(x1, y1, ox, oy) * 0.01,         # separation
            dx1, dy1
        )
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx1, dy1)

    return [int(best_move[0]), int(best_move[1])]