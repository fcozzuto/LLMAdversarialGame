def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources visible, drift to far corner to reduce being blocked
    if not resources:
        tx = gw - 1 if sx < gw // 2 else 0
        ty = gh - 1 if sy < gh // 2 else 0
        best, bestv = [0, 0], -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): continue
            d = cheb(nx, ny, tx, ty)
            v = -d
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Choose a move by targeting the resource where we can arrive sooner than opponent
    best_move, best_val = [0, 0], -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny): continue

        # Evaluate best target from this resulting position
        best_t, best_tv = None, -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Favor: we arrive sooner; tie-break by being closer
            tv = (d_op - d_me, -d_me)
            if tv[0] > best_tv or (tv[0] == best_tv and tv[1] > (0 if best_t is None else 0)):
                best_tv = tv[0]
                best_t = (rx, ry, d_me, d_op)

        rx, ry, d_me, d_op = best_t
        # Also encourage reducing distance to nearest resource overall
        d_self_nearest = min(cheb(nx, ny, r[0], r[1]) for r in resources)

        # Final score: strong advantage, then progress
        val = (d_op - d_me) * 10 - d_self_nearest
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    # Minor anti-stall: if best move doesn't change and there is a strictly better neighbor, pick it next
    if best_move == [0, 0]:
        curr_near = min(cheb(sx, sy, r[0], r[1]) for r in resources)
        improved = None
        for dx, dy in moves:
            if [dx, dy] == [0, 0]: continue
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): continue
            nd = min(cheb(nx, ny, r[0], r[1]) for r in resources)
            if nd < curr_near:
                improved = [dx, dy]
                break
        if improved is not None:
            return improved
    return best_move