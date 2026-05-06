def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def step_dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev for 8-direction moves

    # Choose a resource we can arrive at no later than opponent (deny/secure)
    target = None
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = step_dist(sx, sy, rx, ry)
        opd = step_dist(ox, oy, rx, ry)
        if myd <= opd:
            key = (- (opd - myd), myd, rx, ry)  # maximize margin, then closer
            if best is None or key < best:
                best = key
                target = (rx, ry)

    # If can't deny, just chase closest resource
    if target is None:
        target = min(resources, key=lambda r: step_dist(sx, sy, r[0], r[1]))

    tx, ty = target

    # Pick move that improves toward target, avoids obstacles, and (if needed) increases distance from opponent
    candidates = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_to = step_dist(nx, ny, tx, ty)
        my_now = step_dist(sx, sy, tx, ty)
        # Encourage reducing distance to target; if opponent is closer to many resources, also back off
        opp_now = step_dist(ox, oy, tx, ty)
        opp_after = step_dist(ox, oy, tx, ty)  # opponent stationary in one-step heuristic
        myd_adv = (my_now - my_to)
        opp_spoils = 1 if step_dist(ox, oy, tx, ty) <= step_dist(sx, sy, tx, ty) else 0
        dist_opp = step_dist(nx, ny, ox, oy)
        score = (0, 0, 0, 0)
        # Lexicographic score: maximize advancement, then maximize separation if opponent is also contesting
        key = (
            -(myd_adv),
            opp_spoils * ( -dist_opp ),
            my_to,
            (nx, ny)
        )
        if best_score is None or key < best_score:
            best_score = key
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]