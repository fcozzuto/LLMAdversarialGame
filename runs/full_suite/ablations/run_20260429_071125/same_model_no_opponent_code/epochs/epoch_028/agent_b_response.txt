def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if (sx, sy) in resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose the resource where we are closest relative to the opponent (prefer positive gap).
    if resources:
        best_r = None
        best_gap = -10**9
        for tx, ty in resources:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            gap = od - sd  # positive means we are nearer
            if gap > best_gap or (gap == best_gap and (tx, ty) < (best_r[0], best_r[1])):
                best_gap = gap
                best_r = (tx, ty)
        tx, ty = best_r
    else:
        tx, ty = w // 2, h // 2

    # Evaluate immediate moves deterministically.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # Primary: reduce distance to chosen target
        dist_t = cheb(nx, ny, tx, ty)
        # Secondary: improve relative access to all resources (captures "contesting" behavior)
        rel_sum = 0
        for rx, ry in resources[:12]:
            rel_sum += (cheb(ox, oy, rx, ry) - cheb(nx, ny, rx, ry))
        # Tertiary: avoid allowing opponent to get significantly closer to the same target
        opp_dist_after = cheb(nx, ny, ox, oy)
        val = (1000 - dist_t * 10) + rel_sum - opp_dist_after * 0.05
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]