def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    if w <= 0 or h <= 0:
        return [0, 0]

    # Risk-aware: after one move, pick the move that maximizes "how much sooner we reach some resource than opponent"
    best_move = (0, 0)
    best_val = -10**18
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue
        val = -1  # small bias to avoid staying unless beneficial
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            # Strongly prefer immediate collection; otherwise maximize reach advantage.
            if my_d == 0:
                val += 1000000
            # Margin rewards and tie-breaks toward closer-to-target while keeping opponent far.
            val += (op_d - my_d) * 1000
            val += (50 - my_d)  # prefer smaller my_d
            val += (my_d == 0) * 0  # already handled
        # Secondary: if still tied, prefer increasing distance from opponent (reduce contested swaps).
        opp_dist = cheb(nx, ny, ox, oy)
        val += opp_dist
        if val > best_val:
            best_val = val
            best_move = (mdx, mdy)
    return [int(best_move[0]), int(best_move[1])]