def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not safe(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            key = (-d, dx == 0 and dy == 0, dx, dy)  # maximize approach? (negative distance)
            best = key if best is None or key < best else best
        if best is None:
            return [0, 0]
        # Recover move deterministically from best key by scanning again
        target = best
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if safe(nx, ny):
                d = cheb(nx, ny, ox, oy)
                if (-d, dx == 0 and dy == 0, dx, dy) == target:
                    return [dx, dy]
        return [0, 0]

    # Choose a resource to contest: maximize (opp_dist - self_dist) after one step, then minimize self_dist.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        best_res = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent after our move.
            # Score tuple: (contest advantage, -self_dist, tie-break to avoid staying, then stable ordering).
            contest = od - sd
            # Slightly prefer moves that reduce distance to the currently-best resource even if far away.
            tie = (contest, -sd, abs(dx) + abs(dy), dx, dy)
            if best_res is None or tie > best_res:
                best_res = tie
        # Additional opponent-avoidance: penalize steps that reduce our distance to opponent less than to their closest resource.
        # Deterministic small tie-break term based on relative movement.
        opp_d = cheb(nx, ny, ox, oy)
        score = (best_res[0], best_res[1], -opp_d, -abs(dx) - abs(dy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]