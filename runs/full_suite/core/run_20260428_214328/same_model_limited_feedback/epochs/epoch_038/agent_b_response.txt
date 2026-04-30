def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])

    obs_set = {(p[0], p[1]) for p in obstacles}
    res_list = [(p[0], p[1]) for p in resources]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev for 8-dir moves

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick resource where we have tempo (closer than opponent), else best relative gap.
    best_r = None
    best_score = -10**18
    for r in res_list:
        rd = dist((sx, sy), r)
        od = dist((ox, oy), r)
        # obstacle proximity penalty (prefer open routes)
        px = r[0]; py = r[1]
        neigh = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = px + dx, py + dy
                if (nx, ny) in obs_set:
                    neigh += 1
        # prefer central slightly to prevent being trapped on edges
        cen = abs(px - cx) + abs(py - cy)
        score = (od - rd) * 10 - rd - neigh * 1.5 - cen * 0.02
        if score > best_score:
            best_score = score
            best_r = r

    # If no resources (edge case), drift toward opponent's side of board.
    if best_r is None:
        tx, ty = (w - 1 - ox, h - 1 - oy)
    else:
        tx, ty = best_r

    # Evaluate candidate moves: avoid obstacles, go closer to target, keep distance from opponent.
    best_m = (0, 0)
    best_v = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        myd = dist((nx, ny), (tx, ty))
        opd = dist((nx, ny), (ox, oy))
        # extra avoid: don't step into obstacle-adjacent cells if it doesn't help
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obs_set:
                    adj += 1
        v = -myd * 5 + opd * 0.7 - adj * 0.3
        if v > best_v:
            best_v = v
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]