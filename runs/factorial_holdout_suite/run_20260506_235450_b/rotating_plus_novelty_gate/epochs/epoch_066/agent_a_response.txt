def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return (x, y) in obs or not (0 <= x < w and 0 <= y < h)

    def adj_obstacle_count(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obs:
                    c += 1
        return c

    if not resources:
        return [0, 0]

    # Choose target resource maximizing relative advantage; break ties by sooner self.
    best = None
    best_val = -10**18
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if not (isinstance(rx, int) and isinstance(ry, int)):
            continue
        if blocked(rx, ry):
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Encourage taking when we are ahead, but also prefer closer targets overall.
        val = (do - ds) * 100 - ds - (adj_obstacle_count(rx, ry))
        if val > best_val:
            best_val = val
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    # One-step action selection with obstacle-aware tie-breaking.
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_rank = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        # rank: prioritize moving closer to target; then avoid obstacles; then avoid giving opponent advantage.
        d_to = cheb(nx, ny, tx, ty)
        opp_to = cheb(ox, oy, tx, ty)
        self_adv = (opp_to - d_to)  # higher is better
        rank = (d_to, -self_adv, adj_obstacle_count(nx, ny), (dx != 0 or dy != 0))
        if best_rank is None or rank < best_rank:
            best_rank = rank
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]