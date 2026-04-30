def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        # Pick a resource that maximizes our advantage (opponent far, us close).
        # Tie-break by closer to us, then by deterministic ordering.
        best = None
        best_key = None
        for tx, ty in resources:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            key = (od - sd, -sd, ty, tx)  # maximize advantage; minimize our distance; stable order
            if best_key is None or key > best_key:
                best_key = key
                best = (tx, ty)
        tx, ty = best

    # If our greedy approach is blocked or suboptimal, evaluate one-step moves directly.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Compute score against all resources: maximize advantage after moving,
        # with slight preference for reducing our distance to the chosen target.
        max_adv = -10**9
        for rx, ry in (resources if resources else [(tx, ty)]):
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if adv > max_adv:
                max_adv = adv
        # tie-breakers: prefer closer to chosen target, then nearer to center (stability).
        d_to_target = cheb(nx, ny, tx, ty)
        cx, cy = (w - 1) // 2, (h - 1) // 2
        d_center = cheb(nx, ny, cx, cy)
        score = (max_adv, -d_to_target, -d_center, dy, dx)  # deterministic
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]