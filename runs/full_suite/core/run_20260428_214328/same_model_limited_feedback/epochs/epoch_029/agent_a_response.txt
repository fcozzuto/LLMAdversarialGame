def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    blocked = set((x, y) for x, y in obstacles)

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # If no resources, drift toward opponent's side while staying safe.
    if not resources:
        tx, ty = (w - 1, h - 1) if (sx + sy) < (ox + oy) else (0, 0)
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in blocked:
                continue
            v = -cheb(nx, ny, tx, ty) - 0.2 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Select a resource where we have a timing advantage; break ties toward closer.
    best_res = None
    best_score = -10**18
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # timing advantage first, then prefer closer; small center bias to avoid edge traps
        center_bias = -0.01 * (abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
        score = (od - sd) * 10.0 - sd + center_bias
        if score > best_score:
            best_score = score
            best_res = (rx, ry)

    rx, ry = best_res

    # Greedy step toward target, with mild penalty if it lets opponent gain closer access.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in blocked:
            continue
        # If we are already on a resource, stay (likely to collect) unless a better move exists.
        self_progress = cheb(nx, ny, rx, ry)
        opp_dist = cheb(ox, oy, rx, ry)
        # Our move reduces our distance; penalize moves that don't improve or give opponent advantage.
        v = -self_progress * 3.0
        if self_progress < cheb(sx, sy, rx, ry):
            v += 5.0
        v += (opp_dist - self_progress) * 0.8
        # Avoid moving into positions that are "too close" to opponent when equal progress options exist.
        v -= 0.1 * cheb(nx, ny, ox, oy)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]

    return best_move