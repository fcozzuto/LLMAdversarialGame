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

    target = None
    if resources:
        best = None
        best_score = None
        for rx, ry in resources:
            d = dist_cheb((sx, sy), (rx, ry))
            od = dist_cheb((ox, oy), (rx, ry))
            score = (d, od)
            if best_score is None or score < best_score:
                best = (rx, ry)
                best_score = score
        target = best

    # Simple, solid policy: move toward target if available and not blocked; else move toward center or stay.
    if target is not None:
        tx, ty = target
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        cand = [(dx, dy), (dx, 0), (0, dy)]
        for d in cand:
            nx, ny = sx + d[0], sy + d[1]
            if inside(nx, ny) and (nx, ny) not in obst:
                return [d[0], d[1]]
        # if blocked by obstacles, try other neighboring safe moves
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = sx + ax, sy + ay
                if inside(nx, ny) and (nx, ny) not in obst:
                    return [ax, ay]
        return [0, 0]

    # No resources: move toward center to improve mobility
    cx, cy = w//2, h//2
    dx = 0 if cx == sx else (1 if cx > sx else -1)
    dy = 0 if cy == sy else (1 if cy > sy else -1)
    for d in [(dx, dy), (dx, 0), (0, dy), (1, -1), (-1, -1), (1, 1), (-1, 1), (0, 0)]:
        nx, ny = sx + d[0], sy + d[1]
        if inside(nx, ny) and (nx, ny) not in obst:
            return [d[0], d[1]]
    return [0, 0]