def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    # If no resources, drift toward center to avoid wasting time
    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Evaluate next step by looking at the closest reachable resource distance for both players.
    # Add a penalty for moving adjacent to obstacles to reduce getting trapped.
    best_move = [0, 0]
    best_val = -10**18

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        def nearest_dist(px, py, prefer_block_avoid=True):
            dmin = 10**9
            for r in resources:
                if not r or len(r) < 2:
                    continue
                rx, ry = int(r[0]), int(r[1])
                if not inb(rx, ry) or (rx, ry) in obstacles:
                    continue
                d = cheb(px, py, rx, ry)
                if d < dmin:
                    dmin = d
            if dmin == 10**9:
                dmin = 0
            return dmin

        self_d = nearest_dist(nx, ny)
        opp_d = nearest_dist(ox, oy)

        adj_pen = 0
        if obstacles:
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (nx + ax, ny + ay) in obstacles:
                        adj_pen += 1

        # Primary: maximize relative advantage (opp closer - us closer).
        # Secondary: break ties by preferring smaller self distance, then closer to opponent (to deny).
        val = (opp_d - self_d) * 1000 - self_d - adj_pen * 7 - cheb(nx, ny, ox, oy) * 0.1

        if val > best_val:
            best_val = val
            best_move = [mx, my]

    return best_move