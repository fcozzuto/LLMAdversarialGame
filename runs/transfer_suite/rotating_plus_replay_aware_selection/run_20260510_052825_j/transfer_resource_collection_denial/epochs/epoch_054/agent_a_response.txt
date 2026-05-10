def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    valid = []
    for p in resources:
        rx, ry = p[0], p[1]
        if inb(rx, ry) and (rx, ry) not in obstacles:
            valid.append((rx, ry))
    if not valid:
        return [0, 0]

    # Select target resource maximizing (opp_reach - self_reach), i.e., we arrive first.
    best = None
    for rx, ry in valid:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer positive advantage; then shortest self distance; then farther from opponent.
        key = (-(od - sd), sd, -od, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Greedy step toward target with obstacle and "resource-on-next" preference.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    # Quick set for next-step resource capture
    res_set = set(tuple(p) for p in valid)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        on_res = (nx, ny) in res_set
        # If we can capture next, make it strongly preferred.
        nd = cheb(nx, ny, tx, ty)
        od_next = cheb(ox, oy, tx, ty)
        # Also consider whether this step keeps us closer than opponent to the chosen target.
        behind = nd - od_next
        key = (0 if on_res else 1, nd, behind, abs(dx) + abs(dy), nx, ny)
        if best_m is None or key < best_m[0]:
            best_m = (key, [dx, dy])
    if best_m is None:
        return [0, 0]
    return best_m[1]