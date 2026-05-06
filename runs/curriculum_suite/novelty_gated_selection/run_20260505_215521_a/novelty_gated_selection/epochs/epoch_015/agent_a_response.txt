def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        # Defensive drift away from opponent cornering: maximize distance
        best = None
        for dx, dy, nx, ny in moves:
            opp_d = md(nx, ny, ox, oy)
            key = (-opp_d, dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Pick a "contested" resource: where opponent is relatively closer.
    best_target = None
    best_val = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # Lower value => more opponent pressure vs our reach; tie-break by closer absolute and then lexicographic.
        val = (od - sd, od, rx, ry)
        if best_val is None or val < best_val:
            best_val = val
            best_target = (rx, ry)

    rx, ry = best_target

    # Choose move to approach target while denying opponent after the move.
    best = None
    for dx, dy, nx, ny in moves:
        self_to_t = md(nx, ny, rx, ry)
        opp_to_t = md(ox, oy, rx, ry)
        # Estimate deny: prefer moves that increase our distance from opponent (or at least don't reduce it),
        # and that reduce our time-to-target.
        opp_d = md(nx, ny, ox, oy)
        # Smallest key wins: prioritize target, then maximize opponent distance, then reduce opponent's target advantage.
        deny = (opp_to_t - md(nx, ny, rx, ry))  # larger means we gain more
        key = (self_to_t, -opp_d, -deny, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)
    return [best[1], best[2]]