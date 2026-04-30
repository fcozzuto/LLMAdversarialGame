def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def nearest_dist(x, y):
        if not resources:
            return 0
        best = 10**9
        for r in resources:
            d = cheb((x, y), r)
            if d < best:
                best = d
        return best

    # Prefer making progress to nearest resource while nudging opponent away from theirs
    if resources:
        my_base = nearest_dist(sx, sy)
        op_base = nearest_dist(ox, oy)
    else:
        my_base = op_base = 0

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d = nearest_dist(nx, ny)
        op_d = nearest_dist(ox, oy)  # opponent doesn't move this turn
        # Main: reduce distance; Secondary: prefer moving toward resources that are closer to us than opponent (contested)
        contested = 0
        if resources:
            for r in resources:
                d1 = cheb((nx, ny), r)
                d2 = cheb((ox, oy), r)
                if d1 <= d2:
                    contested += 1
                    if contested >= 2:
                        break
        val = (my_base - my_d) * 2.0 + contested * 0.15 + (op_d - op_base) * 0.05
        # Tiny deterministic bias to centralization when similar
        cx, cy = w // 2, h // 2
        val -= 0.001 * (cheb((nx, ny), (cx, cy)))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]