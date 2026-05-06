def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        ay = y1 - y2
        return ax if ax >= 0 else -ax if ax <= 0 else -ax

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def cell_blocked(x, y):
        return (x, y) in obstacles or not inb(x, y)

    def eval_target(rx, ry):
        # Prefer: we arrive sooner than opponent (resource_denial), avoid being stuck by obstacles.
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        return (do - ds, -ds, - (rx + ry))  # deterministic tie-break

    best_rxry = None
    if resources:
        best_val = None
        for (rx, ry) in resources:
            if cell_blocked(rx, ry):
                continue
            v = eval_target(rx, ry)
            if best_val is None or v > best_val:
                best_val = v
                best_rxry = (rx, ry)

    # If no available resource, head toward opponent's corner along strongest axis.
    if best_rxry is None:
        dx = 0 if sx == ox else (1 if ox > sx else -1)
        dy = 0 if sy == oy else (1 if oy > sy else -1)
        return [dx, dy]

    rx, ry = best_rxry

    # One-step lookahead: choose move maximizing next advantage vs resource, and penalize obstacle collisions.
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds1 = dist((nx, ny), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        adv = do - ds1
        # Deny if we can get closer than opponent; also slightly prefer moving away from opponent when equal.
        opp_rel = dist((nx, ny), (ox, oy)) - dist((sx, sy), (ox, oy))
        # Small bias to continue toward target deterministically.
        toward = -(abs(nx - rx) + abs(ny - ry))
        score = (adv, -ds1, opp_rel, toward, -dx, -dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move