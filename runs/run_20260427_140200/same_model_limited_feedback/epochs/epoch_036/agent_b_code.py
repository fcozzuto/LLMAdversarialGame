def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if (sx, sy) in obstacles:
        obstacles = set()
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def clamp(x, y):
        if x < 0: x = 0
        if y < 0: y = 0
        if x >= w: x = w - 1
        if y >= h: y = h - 1
        return x, y
    def step_dist(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev
    # If no resources, move toward center to reduce stalemate.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = clamp(sx + dx, sy + dy)
            if (nx, ny) in obstacles:
                continue
            v = -step_dist((nx, ny), (tx, ty))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return list(best if best is not None else (0, 0))
    # Choose move that improves access to a resource where we are relatively closer.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        # Immediate pickup if present.
        immediate = 1.0 if (nx, ny) in set(tuple(r) for r in resources) else 0.0
        my_dist_to = []
        opp_dist_to = []
        for rx, ry in resources:
            d_my = step_dist((nx, ny), (rx, ry))
            d_opp = step_dist((ox, oy), (rx, ry))
            my_dist_to.append(d_my)
            opp_dist_to.append(d_opp)
        # Prefer resources where (my_dist - opp_dist) is small/negative.
        min_rel = 10**9
        min_my = 10**9
        for d_my, d_opp in zip(my_dist_to, opp_dist_to):
            rel = d_my - d_opp
            if rel < min_rel:
                min_rel = rel
            if d_my < min_my:
                min_my = d_my
        # Obstacle avoidance: penalize being adjacent to obstacles.
        adj_pen = 0
        for oxp in (-1, 0, 1):
            for oyp in (-1, 0, 1):
                if oxp == 0 and oyp == 0:
                    continue
                axp, ayp = nx + oxp, ny + oyp
                if 0 <= axp < w and 0 <= ayp < h and (axp, ayp) in obstacles:
                    adj_pen += 1
        # Also mildly prefer moves that reduce distance to opponent to enable block by collision if tied.
        to_opp = step_dist((nx, ny), (ox, oy))
        # Final value: larger is better.
        v = (2000.0 * immediate) + (-50.0 * min_rel) + (-2.5 * min_my) + (-0.8 * adj_pen) + (-0.01 * to_opp)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]