def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose target: prioritize nearest resource we can beat opponent on; otherwise nearest resource.
    best = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If we arrive first, strongly prefer. If tied, prefer one farther from opponent (reduces contest).
        win_bias = 1000 if ds < do else 0
        tie_bias = 100 if ds == do else 0
        far_from_opp = -cheb(ox, oy, rx, ry)
        center_bonus = -cheb(rx, ry, w // 2, h // 2)  # mild: keep nearer center long-term
        key = (-(win_bias + tie_bias), ds, -far_from_opp, -center_bonus, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))

    # If no resources, move to reduce distance to opponent's line: deterministic drift to mid.
    if best is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best[1]

    # Evaluate next moves: go toward target; avoid squares that allow opponent to get strictly closer next.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_t = cheb(nx, ny, tx, ty)
        d_o_now = cheb(ox, oy, tx, ty)
        d_o_next_best = 10**9
        for odx, ody in dirs:
            mx, my = ox + odx, oy + ody
            if valid(mx, my):
                d_o_next_best = min(d_o_next_best, cheb(mx, my, tx, ty))
        # Penalize if we move into a state where opponent can get closer to target than we can maintain.
        my_to_target_next = d_t
        opp_close_penalty = 0
        if d_o_next_best < d_o_now and my_to_target_next >= d_o_next_best:
            opp_close_penalty = 50
        # Also keep away from obstacles already handled by validity; mild repulsion from opponent position.
        opp_dist = cheb(nx, ny, ox, oy)
        repulse = 0 if opp_dist >= 2 else (6 - opp_dist) * 3
        # Deterministic tie-break uses dx,dy lexicographic.
        score = (my_to_target_next + opp_close_penalty + repulse, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]