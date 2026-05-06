def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        if dx < 0: dx = -dx
        dy = by - ay
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obstacle_pen(x, y):
        dmin = 10
        for (px, py) in obs:
            d = cheb(x, y, px, py)
            if d < dmin:
                dmin = d
                if dmin == 0:
                    break
        if dmin >= 3:
            return 0
        return (3 - dmin) * 2

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # drift slightly away from obstacles toward center if available
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        tx = 0 if sx == int(cx) else (1 if sx < int(cx) else -1)
        ty = 0 if sy == int(cy) else (1 if sy < int(cy) else -1)
        return [tx, ty]

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
        # prefer taking resources that are closer to us than to opponent, while keeping distance reasonable
        val = -obstacle_pen(nx, ny)
        cur = 0
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # main: closeness
            s = -d_me
            # tactical: beat opponent to the resource
            s += 0.8 * (d_opp - d_me)
            # slight preference for nearer overall targets
            if d_me <= 1:
                s += 2
            cur = s if d_me == 0 else (cur if cur > s else s)
            # (cur tracks best resource score among all)
        val += cur
        # small anti-stalemate: prefer moving if it improves best resource score
        if (dx, dy) != (0, 0):
            val += 0.1 * (1 - cheb(sx, sy, ox, oy) * 0.0)
        if val > best_val:
            best_val = val
            best_move = [dx if (0 <= sx + dx < w and (sx + dx, sy) not in obs) else dx, dy if (0 <= sy + dy < h and (sx, sy + dy) not in obs) else dy]
            # ensure dx/dy are within allowed set already; also ensure not invalid by collision/outside
            # if invalid, engine keeps in place anyway; keep chosen dx/dy as computed
    return best_move