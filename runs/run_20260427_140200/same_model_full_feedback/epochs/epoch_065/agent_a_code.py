def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_adv(x, y):
        if not resources:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            return -((x - cx) * (x - cx) + (y - cy) * (y - cy))
        best = -10**9
        for rx, ry in resources:
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            gain = (do - ds) * 3 - ds
            # Prefer closer tie-breaking deterministically
            if do == ds:
                gain -= (rx + ry) * 0.0001
            if gain > best:
                best = gain
        return best

    best_move = (0, 0)
    best_val = -10**18

    # Deterministic iteration order already fixed by dirs list
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = best_adv(nx, ny)
        # Small deterministic bias to avoid oscillation: prefer moves that reduce dist to chosen best target advantage
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If all candidate moves blocked (shouldn't happen), stay
    return [int(best_move[0]), int(best_move[1])]