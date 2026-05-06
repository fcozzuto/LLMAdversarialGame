def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Predict opponent's current greedy target and next move; then intercept that target.
    best_r = None
    best_md = 10**18
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if d < best_md or (d == best_md and (rx, ry) < best_r):
            best_md = d
            best_r = (rx, ry)
    tx, ty = best_r

    opp_next = (ox, oy)
    opp_best = 10**18
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if d < opp_best or (d == opp_best and (nx, ny) < opp_next):
            opp_best = d
            opp_next = (nx, ny)

    oxn, oyn = opp_next
    # Choose our move that minimizes (our distance - opponent next distance) to the target;
    # tie-break by staying away from opponent and keeping closer to target.
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        our_d = cheb(nx, ny, tx, ty)
        opp_d_next = cheb(oxn, oyn, tx, ty)
        key = (our_d - opp_d_next, our_d, -cheb(nx, ny, oxn, oyn), (nx, ny))
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]