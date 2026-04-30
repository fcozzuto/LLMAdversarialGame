def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        # deterministic: move toward opponent while keeping out of obstacles
        best = (0, 0)
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if (dx == 0 and dy == 0) or (inb(nx, ny) and (nx, ny) not in obstacles):
                # prefer reducing distance to opponent, slightly avoid getting closer to center if blocked
                score = -(cheb(nx, ny, ox, oy))
                if score > best_score:
                    best_score, best = score, (dx, dy)
        return [best[0], best[1]]

    # choose resource: maximize advantage (opponent later) and minimize our time
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    best_r = None
    best_r_score = -10**18
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        advantage = d_op - d_me  # positive means we arrive earlier
        # tie-break by preferring resources closer to center
        center_bias = -((rx - cx) * (rx - cx) + (ry - cy) * (ry - cy)) * 0.01
        score = advantage * 100.0 - d_me + center_bias
        if score > best_r_score:
            best_r_score = score
            best_r = (rx, ry)

    rx, ry = best_r

    # If we are not competitive, switch target to nearest resource for us (but still deterministically)
    d_me_now = cheb(sx, sy, rx, ry)
    if best_r_score < 0:
        rx2, ry2 = resources[0]
        dmin = cheb(sx, sy, rx2, ry2)
        for r in resources[1:]:
            rr_x, rr_y = r
            d = cheb(sx, sy, rr_x, rr_y)
            if d < dmin or (d == dmin and (rr_x, rr_y) < (rx2, ry2)):
                dmin, rx2, ry2 = d, rr_x, rr_y
        rx, ry = rx2, ry2
        d_me_now = dmin

    # choose move that improves our progress to target; secondarily makes opponent's progress harder
    best = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ((dx == 0 and dy == 0) or (inb(nx, ny) and (nx, ny) not in obstacles)):
            continue
        d_me_next = cheb(nx, ny, rx, ry)
        d_op_next = cheb(ox, oy, rx, ry)
        # small bias: if our move also changes relative position, it may affect future; approximate by checking our move only
        score = (d_me_now - d_me_next) * 10.0
        # block: if we can come closer while opponent is still far, score more
        d_op_now = cheb(ox, oy, rx, ry)
        if d_op_now > d_me_next:
            score += 200.0
        # deterrence: prefer moves that don't allow opponent to be significantly closer (use our resulting position as a proxy)
        score += -0.3 * d_op_next
        # deterministic tiebreak: prefer