def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obst:
                resources.append((x, y))

    def dist_cheb(a, b):
        dx = abs(a[0]-b[0]); dy = abs(a[1]-b[1])
        return dx if dx>dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if resources:
        # choose closest resource, break ties by prioritizing moving away from opponent when equal
        best = None
        best_score = None
        for rx, ry in resources:
            d = dist_cheb((sx, sy), (rx, ry))
            od = dist_cheb((ox, oy), (rx, ry))
            score = (d, -od)
            if best_score is None or score < best_score:
                best_score = score
                best = (rx, ry)
        tx, ty = best
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obst or not inside(nx, ny):
            # try alternative step: move toward center to dodge
            cx, cy = w // 2, h // 2
            dx = 0 if cx == sx else (1 if cx > sx else -1)
            dy = 0 if cy == sy else (1 if cy > sy else -1)
            nx, ny = sx + dx, sy + dy
        return [dx, dy]

    # No resources: simple deterministic strategy
    # Move to center when safe, else drift toward center
    cx, cy = w // 2, h // 2
    dx = 0 if cx == sx else (1 if cx > sx else -1)
    dy = 0 if cy == sy else (1 if cy > sy else -1)
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obst or not inside(nx, ny):
        # try to step away from opponent slightly
        ax = -1 if ox < sx else (1 if ox > sx else 0)
        ay = -1 if oy < sy else (1 if oy > sy else 0)
        dx, dy = ax, ay
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obst or not inside(nx, ny):
            dx, dy = 0, 0
    return [dx, dy]