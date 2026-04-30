def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                resources.append((rx, ry))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx, cy = w // 2, h // 2
    best_target = (cx, cy)
    best_score = -10**9

    if resources:
        # Race heuristic: pick resource where we gain distance advantage over opponent.
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer closer wins; penalize long travel slightly.
            score = (do - ds) * 10 - ds
            if score > best_score:
                best_score = score
                best_target = (rx, ry)

        # If opponent is clearly closer to our chosen target, switch to intercept (center control).
        ds = cheb(sx, sy, best_target[0], best_target[1])
        do = cheb(ox, oy, best_target[0], best_target[1])
        if do <= ds:
            # Center bias: reduce opponent capture by moving toward mid.
            best_target = (cx, cy)

    tx, ty = best_target
    best_move = (0, 0)
    best_pair = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        d_to_opp = cheb(nx, ny, ox, oy)
        # Primary: get closer to target; Secondary: stay away from opponent less (smaller d_to_opp) breaks ties.
        pair = (d_to_target, d_to_opp)
        if best_pair is None or pair < best_pair:
            best_pair = pair
            best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]