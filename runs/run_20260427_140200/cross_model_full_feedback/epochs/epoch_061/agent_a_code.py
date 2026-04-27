def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

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

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # Choose deterministically based on one-step evaluation.
    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Avoid getting too close to opponent unless it helps capture a resource.
        opp_dist = cheb(nx, ny, ox, oy)
        opp_pen = 0 if opp_dist > 1 else (5 - opp_dist) * 2

        if resources:
            # Evaluate taking the best available resource while considering opponent race.
            v = -opp_pen
            # Tie-breaker prefers moving toward grid center to reduce oscillations.
            v += -abs(nx - cx) - abs(ny - cy)
            for rx, ry in resources:
                d_me = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                # If opponent is closer, reduce priority; if we are closer, increase.
                race = d_opp - d_me
                # Higher is better; also prefer shorter path.
                v += race * 2 - d_me * 0.5
            # Small preference for exact landing on a resource.
            for rx, ry in resources:
                if nx == rx and ny == ry:
                    v += 200
                    break
        else:
            # No resources: move to center while staying away from opponent.
            v = -abs(nx - cx) - abs(ny - cy) - opp_pen * 3

        if best is None or v > bestv:
            bestv = v
            best = [dx, dy]

    return best if best is not None else [0, 0]