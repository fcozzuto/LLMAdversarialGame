def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("runner" in role) or ("flee" in role)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def free_neighbors(x, y):
        c = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obs:
                c += 1
        return c

    def obstacle_adj_pen(x, y):
        p = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs:
                p -= 3
        return p

    target_corner = max(corners, key=lambda c: man(c[0], c[1], ox, oy)) if is_evader else min(corners, key=lambda c: man(c[0], c[1], ox, oy))
    tx, ty = target_corner

    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            val = -10**9 if is_evader else 10**9
        else:
            d_op = man(nx, ny, ox, oy)
            d_tc = man(nx, ny, tx, ty)
            fn = free_neighbors(nx, ny)
            pen = obstacle_adj_pen(nx, ny)
            if is_evader:
                # Prefer moving away from pursuer and toward farthest corner, while staying mobile.
                val = d_op + 0.3 * fn - 0.05 * d_tc + pen * 0.05
            else:
                # Prefer reducing distance to pursuer and getting to a closer corner, while not trapping.
                val = -(d_op + 0.02 * d_tc) + 0.2 * fn + pen * 0.05

        if best_val is None or (val > best_val if is_evader else val < best_val):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]