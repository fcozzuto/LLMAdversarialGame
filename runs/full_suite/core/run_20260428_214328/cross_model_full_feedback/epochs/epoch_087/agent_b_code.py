def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    # If there are resources, move toward the closest resource while avoiding obstacles.
    if resources:
        sxr, syr = sx, sy
        best = None
        bestd = 10**9
        for r in resources:
            d = cheb((sxr, syr), r)
            if d < bestd:
                bestd = d
                best = r
        if best is not None:
            tx, ty = best
            dx = 0 if tx == sx else (1 if tx > sx else -1)
            dy = 0 if ty == sy else (1 if ty > sy else -1)
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
            # try alternative moves toward resource if blocked
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    cx, cy = sx + ax, sy + ay
                    if valid(cx, cy):
                        if cheb((cx, cy), best) < cheb((sx, sy), best):
                            return [ax, ay]

    # Fallback: move away from opponent along a safe path, prioritizing axis-aligned moves
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        # discourage moving toward opponent
        d_op = cheb((nx, ny), (ox, oy))
        d_me = cheb((nx, ny), (sx, sy))
        score = d_op - d_me
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    if best_move is not None:
        return [best_move[0], best_move[1]]

    # As last resort stay
    return [0, 0]