def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def min_dist_to_resources(x, y):
        if not resources:
            return 10**9
        best = 10**9
        for tx, ty in resources:
            d = cheb(x, y, tx, ty)
            if d < best:
                best = d
        return best

    if resources:
        best_move = (0, 0)
        best_score = -10**18
        opp_best = min_dist_to_resources(ox, oy)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            self_best = min_dist_to_resources(nx, ny)
            on_resource = 1 if (nx, ny) in resources else 0
            # maximize advantage over opponent; reward stepping onto resource
            score = (opp_best - self_best) + 20 * on_resource
            # break ties toward moving closer to opponent (more pressure)
            score += 0.01 * cheb(nx, ny, ox, oy) * -1
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: converge to center while keeping distance from opponent's corner pressure
    cx, cy = W // 2, H // 2
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Prefer smaller distance to center; if tied, prefer larger distance from opponent
        score = -cheb(nx, ny, cx, cy) + 0.001 * cheb(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]