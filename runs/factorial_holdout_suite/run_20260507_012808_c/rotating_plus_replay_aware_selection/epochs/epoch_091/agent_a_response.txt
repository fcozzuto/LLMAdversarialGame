def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def center_target():
        return (w - 1) // 2, (h - 1) // 2

    if not resources:
        tx, ty = center_target()
        best = [0, 0]
        bestv = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d < bestv:
                    bestv = d
                    best = [dx, dy]
        return best

    best_move = [0, 0]
    best_score = -10**18

    opp_dist_cache = {}
    for rx, ry in resources:
        opp_dist_cache[(rx, ry)] = cheb(ox, oy, rx, ry)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        move_score = -10**18
        for rx, ry in resources:
            od = opp_dist_cache[(rx, ry)]
            nd = cheb(nx, ny, rx, ry)
            if nd == 0:
                score = 1000000 + (od * 0.1)
            else:
                # Want small nd, large od (reach first), and slight preference for nearer overall.
                lead = od - nd
                score = (lead * 50.0) - (nd * 2.0) + (od * 0.1)
                # If opponent is already strictly closer, de-prioritize but don't fully discard.
                if lead < 0:
                    score -= 30.0
            if score > move_score:
                move_score = score
        # Tie-break: prefer moves with smaller our best distance, then smaller dx/dy lexicographically
        if move_score > best_score:
            best_score = move_score
            best_move = [dx, dy]
        elif move_score == best_score:
            cur_best_nd = cheb(sx + best_move[0], sy + best_move[1], resources[0][0], resources[0][1])
            new_best_nd = cheb(nx, ny, resources[0][0], resources[0][1])
            if new_best_nd < cur_best_nd or (new_best_nd == cur_best_nd and [dx, dy] < best_move):
                best_move = [dx, dy]

    return best_move