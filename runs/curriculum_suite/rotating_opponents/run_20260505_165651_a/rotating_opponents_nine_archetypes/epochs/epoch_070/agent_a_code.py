def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    cx, cy = (w - 1) // 2, (h - 1) // 2
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = [m for m in moves if not blocked(sx + m[0], sy + m[1])]
    if not moves:
        return [0, 0]

    if not resources:
        # Center-and-aversion: prefer decreasing center distance while increasing opp distance
        bestm = moves[0]
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = (md(nx, ny, cx, cy), -md(nx, ny, ox, oy))
            if bestv is None or v < bestv:
                bestv, bestm = v, (dx, dy)
        return [bestm[0], bestm[1]]

    # Evaluate only a few most relevant resources (closest to us)
    rs = []
    for r in resources:
        rx, ry = r
        rs.append((md(sx, sy, rx, ry), rx, ry))
    rs.sort(key=lambda t: t[0])
    rs = rs[:4]

    # Move scoring: chase resource but avoid giving opponent a faster (or equal) route to it.
    bestm = moves[0]
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        my_center = md(nx, ny, cx, cy)
        my_opp = md(nx, ny, ox, oy)
        v_best = None
        for _, rx, ry in rs:
            myd = md(nx, ny, rx, ry)
            oppd = md(ox, oy, rx, ry)
            # If opponent can reach as fast or faster, strongly penalize unless we're also very close to center.
            reach_diff = oppd - myd  # positive if we're closer than opponent
            block = 0
            if oppd <= myd:
                block = 10 + (myd == 0) * 6
            # Bonus for nearing target, but only if not simultaneously enabling opponent.
            # Small additional bonus for moving toward center to avoid being edge-patrolled.
            score = (reach_diff * 3) - myd - block + (6 - my_center) + (2 if my_opp >= 3 else 0)
            if v_best is None or score > v_best:
                v_best = score
        cand = (v_best, my_center, -my_opp)
        if bestv is None or cand > bestv:
            bestv, bestm = cand, (dx, dy)

    return [bestm[0], bestm[1]]