def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Target resources by advantage (we prefer resources we can reach sooner)
    best_r = None
    best_adv = -10**9
    best_selfd = 10**9
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        adv = d_op - d_me
        if adv > best_adv or (adv == best_adv and (d_me < best_selfd or (d_me == best_selfd and (rx, ry) < best_r))):
            best_adv = adv
            best_selfd = d_me
            best_r = (rx, ry)
    tx, ty = best_r

    # Move that maximizes (advantage after move), with deterministic tie-breaks
    best_score = -10**18
    best_delta = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_me = cheb(nx, ny, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        # Secondary preference: also reduce distance to our chosen target
        score = (d_op - d_me) * 1000 - d_me
        # Small deterministic tie-break on direction order
        if score > best_score:
            best_score = score
            best_delta = [dx, dy]
    return best_delta if ok(sx + best_delta[0], sy + best_delta[1]) else [0, 0]