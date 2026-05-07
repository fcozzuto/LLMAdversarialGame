def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            cx, cy = int(r[0]), int(r[1])
            if (cx, cy) not in obstacles:
                resources.append((cx, cy))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    # Deny/secure objective: maximize (opp_dist - self_dist), with a small push to reach sooner.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_step_dist = 0
        target_gain = -10**18
        target_reach = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            gain = do - ds  # positive means we can get there no later than opponent
            if gain > target_gain or (gain == target_gain and (ds < target_reach or (ds == target_reach and rx + ry < self_step_dist))):
                target_gain = gain
                target_reach = ds
                self_step_dist = rx + ry
        # If we can secure some resource, prioritize highest gain then fastest reach.
        # Otherwise, prioritize closest resource with slight deterministic tie-break.
        parity_bias = ((nx + ny) & 1) * 0.001
        val = target_gain * 1000.0 - target_reach + parity_bias
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]