def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def min_dist_to_resources(px, py):
        if not resources:
            return 10**9
        best = 10**9
        for rx, ry in resources:
            d = cheb(px, py, rx, ry)
            if d < best:
                best = d
        return best

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if resources:
            self_d = min_dist_to_resources(nx, ny)
            opp_d = min_dist_to_resources(ox, oy)
            val = (opp_d - self_d) * 10
            # Small tie-breaker: prefer moving toward the closest resource and slightly away from opponent
            # (compute against the closest resource to us only)
            if self_d < 10**9:
                closest = None
                for rx, ry in resources:
                    if cheb(nx, ny, rx, ry) == self_d:
                        closest = (rx, ry)
                        break
                if closest is not None:
                    cx, cy = closest
                    val += -cheb(nx, ny, cx, cy)
            val += -cheb(nx, ny, ox, oy) * 0.01
        else:
            # No resources: drift to center while keeping some distance from opponent
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            val = -(abs(nx - cx) + abs(ny - cy)) - cheb(nx, ny, ox, oy) * 0.001
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]