def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick a target that I can reach relatively before the opponent.
    best_t = resources[0]
    best_key = None
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Prefer closer resources, but also avoid ones opponent is much nearer to.
        key = (d_me, d_op - d_me, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)
    tx, ty = best_t

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Also steer to make it harder for opponent to take their closest resource.
    def opp_best_dist(px, py):
        md = 10**9
        for rx, ry in resources:
            d = cheb(px, py, rx, ry)
            if d < md:
                md = d
        return md

    base_opp = opp_best_dist(ox, oy)
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        # My progress to target and slight preference to reduce distance to any resource.
        my_d = cheb(nx, ny, tx, ty)
        my_any = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < my_any:
                my_any = d

        # Opponent "pressure": if I'm closer to my target, I want to reduce their ability to access theirs.
        # Approx: use opponent best distance growth if I move closer to the global center of remaining resources.
        # Deterministic proxy: prefer moves that increase Manhattan/cheb separation between me and opponent
        # while still making progress to my target.
        sep = cheb(nx, ny, ox, oy)
        score = (-my_d) + (-0.2 * my_any) + (0.05 * sep)
        # Strongly discourage wasting moves away from target.
        if my_d > cheb(sx, sy, tx, ty):
            score -= 0.6

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move