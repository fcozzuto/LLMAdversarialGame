def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def steps_approx(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        # Chebyshev steps on 8-neighborhood
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1,  0), (0,  0), (1,  0),
             (-1,  1), (0,  1), (1,  1)]

    # If no resources, head to the corner that our start is "closer to" than opponent
    if not resources:
        tx = 0 if sx <= ox else w - 1
        ty = 0 if sy <= oy else h - 1
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            key = (dist2(nx, ny, tx, ty), dist2(nx, ny, ox, oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    # Choose a target resource to maximize opponent delay relative to us; then pick next move
    # that improves our chance while also keeping distance from the opponent (separation).
    best_move = None
    best_key = None

    def target_value(rx, ry):
        st = steps_approx((sx, sy), (rx, ry))
        ot = steps_approx((ox, oy), (rx, ry))
        return (ot - st, -dist2(sx, sy, rx, ry), rx, ry)  # prefer larger advantage, then closer tie-break

    # Pick a single deterministic target: best by advantage; if tie, closer to us; then lower coords
    best_t = None
    for rx, ry in resources:
        val = target_value(rx, ry)
        if best_t is None or val > best_t[0]:
            best_t = (val, (rx, ry))
    tx, ty = best_t[1]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        my_steps = steps_approx((nx, ny), (tx, ty))
        opp_steps = steps_approx((ox, oy), (tx, ty))
        advantage = opp_steps - my_steps

        # Separation term: prefer moves that increase distance from opponent (prevents opponent grabbing same tempo)
        sep = dist2(nx, ny, ox, oy)

        # Small penalty for moving toward obstacles would be redundant; already filtered by ok()
        # Deterministic tie-break: coordinates then move deltas
        key = (advantage, sep, -dist2(nx, ny, tx, ty), nx, ny, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]