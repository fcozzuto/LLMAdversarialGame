def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # If no resources, drift away from opponent while staying generally centered
    if not resources:
        tx = (w - 1) / 2.0 - (ox - sx) * 0.2
        ty = (h - 1) / 2.0 - (oy - sy) * 0.2
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            # Prefer moving away when adjacent
            adj_pen = 4 if cheb(nx, ny, ox, oy) <= 1 else 0
            score = adj_pen + cheb(nx, ny, tx, ty) + (0.01 * (nx - tx) * (nx - tx) + 0.01 * (ny - ty) * (ny - ty))
            if best is None or score < best[0]:
                best = (score, dx, dy)
        if best is None:
            return [0, 0]
        return [int(best[1]), int(best[2])]

    # Choose resource where we can beat opponent (smallest (our_dist - opp_dist), tie by closer to us)
    best_res = None
    best_key = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        d_us = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        key = (d_us - d_op, d_us, abs(rx - sx) + abs(ry - sy), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res
    cur_d = cheb(sx, sy, rx, ry)

    # Greedy step: minimize our dist to target, but avoid stepping into/adjacent to opponent when not improving
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_new = cheb(nx, ny, rx, ry)
        opp_adj = cheb(nx, ny, ox, oy) <= 1
        improve = d_new < cur_d
        # If not improving, strongly discourage moving closer to opponent
        opp_closer = cheb(nx, ny, ox, oy) < cheb(sx, sy, ox, oy)
        pen = 0
        if opp_adj and not improve:
            pen += 100
        if opp_closer and not improve:
            pen += 30
        # Slightly prefer not leaving ourselves stranded behind obstacles: penalize high obstacle density nearby
        local_obs = 0
        for ddx, ddy in deltas:
            tx, ty = nx + ddx, ny + ddy
            if (tx, ty) in obs:
                local_obs += 1
        score = pen + d_new * 10 + local_obs
        if best is None or score < best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]