def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            # Choose move that both gets us close and keeps opponent far from the most contested resource
            val = -10**18
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Main objective: maximize opponent distance advantage while minimizing our distance
                cur = (do - ds) * 100 - ds
                if cur > val:
                    val = cur
            # Small tie-break: prefer moving generally toward opponent side when equally contested
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
            elif val == best_val:
                # deterministic tie-breaker: lexicographic on (dx,dy) with a directionality bias
                if (dx, dy) < best_move:
                    best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        # No visible resources: head toward opponent to deny/control
        tx, ty = ox, oy
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, tx, ty)
            if -d > best_val:
                best_val = -d
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]