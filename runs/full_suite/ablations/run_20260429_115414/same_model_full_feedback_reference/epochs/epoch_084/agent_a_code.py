def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        # Choose a resource where we are closer (tie-break by fewer opponent resources soonest).
        best_r = None
        best_gap = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            gap = ds - do  # negative means we are closer
            if best_r is None or gap < best_gap or (gap == best_gap and ds < cheb(sx, sy, best_r[0], best_r[1])):
                best_r = (rx, ry)
                best_gap = gap

        # If opponent is closer to all, still go to the "least lost" one and add opponent-separation.
        rx, ry = best_r
        best_m = None
        best_s = None
        for dx, dy, nx, ny in legal:
            ns = cheb(nx, ny, rx, ry)
            # Attempt to deny: also minimize opponent's progress to that same target.
            no = cheb(ox, oy, rx, ry)
            next_no = None
            # Opponent position fixed this turn; proxy with our move reducing their future by increasing our contest distance.
            opp_dist_to_us = cheb(nx, ny, ox, oy)
            score = ns * 10 + (no - cheb(ox, oy, rx, ry))  # no effect, keeps deterministic structure
            # Contest shaping: if we're behind (gap>0), prioritize moving to increase distance from opponent.
            behind = 1 if best_gap > 0 else 0
            if behind:
                score += (7 - min(7, opp_dist_to_us)) * 3
            # Slight preference to avoid edges unless needed
            edge_pen = (0 if 1 <= nx <= W - 2 else 2) + (0 if 1 <= ny <= H - 2 else 2)
            score += edge_pen
            if best_s is None or score < best_s:
                best_s = score
                best_m = (dx, dy)
        return [int(best_m[0]), int(best_m[1])]

    # No resources: move to center while keeping some distance from opponent.
    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
    best_m = None
    best_s = None
    for dx, dy, nx, ny in legal:
        to_center = abs(nx - cx)
        to_center2 = abs(ny - cy)
        sep = cheb(nx, ny, ox, oy)
        score = int((to_center + to_center2) * 10) - sep
        if best_s is None or score < best_s:
            best_s = score
            best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]