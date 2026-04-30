def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If resources exist: race towards the best target for us, while pushing away from opponent.
    # If none: move toward center while avoiding opponent line.
    best_move = (0, 0)
    best_score = -10**9

    tx_list = resources if resources else [(int((w - 1) / 2.0), int((h - 1) / 2.0))]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d_op_next = cheb(nx, ny, ox, oy)
        center_x, center_y = int((w - 1) / 2.0), int((h - 1) / 2.0)
        d_center = cheb(nx, ny, center_x, center_y)

        # Score best target we can plausibly reach sooner than opponent.
        local = -10**9
        for tx, ty in tx_list:
            d_me = cheb(nx, ny, tx, ty)
            d_op = cheb(ox, oy, tx, ty)
            # Higher is better: bigger lead (opponent farther than us), also prefer closer.
            lead = d_op - d_me
            reach_bonus = 8 if (nx == tx and ny == ty) else 0
            # If resources: prioritize immediate lead; if no resources: just center.
            base = lead * 10 - d_me
            if resources:
                base += reach_bonus
            else:
                base = -d_center
            # Small deterministic tie-break favoring "earlier" tiles: lexicographic
            base += -(tx * 0.01 + ty * 0.001)
            if base > local:
                local = base

        # Additional global opponent-avoidance: keep some space to reduce contest swaps.
        score = local + (2.5 * d_op_next) * (1 if resources else 0.5)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]