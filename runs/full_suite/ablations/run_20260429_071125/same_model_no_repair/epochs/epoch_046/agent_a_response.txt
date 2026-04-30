def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = [0, 0]
    best_val = -10**18

    # Deterministic tie-break: prefer moves earlier in deltas order.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate: choose target resource that maximizes our advantage after this move.
        # Advantage is opponent_distance - our_distance (larger is better).
        # If we can reach within 1, heavily prioritize it; otherwise prioritize denying.
        move_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            us = cheb(nx, ny, rx, ry)
            op = cheb(ox, oy, rx, ry)
            # If we are strictly closer, prioritize strongly; if not, still deny by reducing their lead.
            adv = op - us
            # Center bias to avoid oscillations
            cb = - (abs(nx - cx) + abs(ny - cy)) * 0.01
            if us <= 1:
                val = 1_000_000 + adv * 10_000 - us * 100 + cb
            else:
                # Encourage cutting: if they are closer, choose targets where their advantage is smallest (adv low/negative).
                val = adv * 8_000 - us * 60 + op * 5 + cb
            if val > move_best:
                move_best = val

        # Small penalty for moving away from the current best region: discourage stepping into worse global position.
        # Use min distance to any resource as a quick global metric.
        min_dist = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = cheb(nx, ny, rx, ry)
            if d < min_dist:
                min_dist = d
        global_val = move_best - min_dist * 40

        if global_val > best_val:
            best_val = global_val
            best_move = [dx, dy]

    return best_move if best_move in ([[-1,-1],[0,-1],[1,-1],[-1,0],[0,0],[1,0],[-1,1],[0,1],[1,1]][i] for i in range(9)) else [0, 0]