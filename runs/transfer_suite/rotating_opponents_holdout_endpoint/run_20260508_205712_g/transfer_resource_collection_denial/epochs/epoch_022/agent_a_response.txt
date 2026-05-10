def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = [tuple(r) for r in observation.get("resources", [])]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # Switch heuristic: prefer resources where we are closer in Manhattan; if behind, take the closest "swing" resource.
    # Also add mild center preference to reduce getting funneled.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    tx, ty = resources[0]
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        center = - (abs(rx - cx) + abs(ry - cy))
        # If we're behind, push to farther-from-opponent resources; if ahead, push to nearer ones.
        swing = (opd - myd)  # positive => we are closer
        key = (swing, -myd, center, -cheb(sx, sy, rx, ry))
        if best is None or key > best:
            best = key
            tx, ty = rx, ry

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    avoid_opponent = cheb(sx, sy, ox, oy) <= 1

    best_score = None
    best_move = [0, 0]
    cur_to = man(sx, sy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        myd = man(nx, ny, tx, ty)
        # Encourage progress to target; if opponent is adjacent, also discourage moving toward them.
        oppd = man(nx, ny, ox, oy)
        # Prefer not getting worse too much while contesting.
        score = (-(myd), (cur_to - myd), oppd if avoid_opponent else 0, -cheb(nx, ny, tx, ty))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move