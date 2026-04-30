def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    # Obstacles
    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    # Resources
    resources = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return max(dx, dy)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Evaluate moves
    moves = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny): 
            continue
        if (nx, ny) in obst:
            continue
        # Basic scoring: prefer moving toward nearest resource, while keeping distance from opponent reasonable
        score = 0
        if resources:
            # distance to closest resource
            d_to_res = min(dist((nx, ny), r) for r in resources)
            d_op = dist((nx, ny), (ox, oy))
            score = -d_to_res*2 + d_op  # bias toward resources but avoid giving up distance to opponent
        else:
            # no resources: approach center-ish away from opponent slightly
            dxo = abs(nx - ox)
            dyo = abs(ny - oy)
            score = -(dxo + dyo)

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]