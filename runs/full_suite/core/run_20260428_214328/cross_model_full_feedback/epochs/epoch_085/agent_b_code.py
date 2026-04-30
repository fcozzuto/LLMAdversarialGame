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
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    # If there are resources, deterministically move toward the closest resource
    if resources:
        best = None
        best_score = -10**9
        for r in resources:
            d_me = cheb((sx, sy), r)
            d_op = cheb((ox, oy), r)
            score = (d_op - d_me) * 10 - d_me
            if score > best_score:
                best_score = score
                best = r
        if best is not None:
            dx = 1 if best[0] > sx else -1 if best[0] < sx else 0
            dy = 1 if best[1] > sy else -1 if best[1] < sy else 0
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]

    # Otherwise, try to move toward center while avoiding obstacles and staying deterministic
    target_x = w // 2
    target_y = h // 2
    dx = 1 if target_x > sx else -1 if target_x < sx else 0
    dy = 1 if target_y > sy else -1 if target_y < sy else 0
    # Prefer moving in a way that reduces distance to center, consider all 9 options in fixed order
    moves = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            return [mx, my]

    # If blocked, stay
    return [0, 0]