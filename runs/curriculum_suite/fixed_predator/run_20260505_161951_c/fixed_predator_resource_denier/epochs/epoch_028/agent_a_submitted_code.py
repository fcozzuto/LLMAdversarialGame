def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obstacle_set = set(obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacle_set

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_move = (0, 0)
    best_score = -10**18

    if resources:
        target = None
        best_r = 10**18
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best_r:
                best_r = d
                target = (rx, ry)
        tx, ty = target
        myd = best_r
        od = cheb(ox, oy, tx, ty)
        seek = 1 if myd <= od else -1  # if behind, try to deny by moving toward it anyway but weight opponent blocking
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            nd = cheb(nx, ny, tx, ty)
            score = -nd * 10 + (cheb(nx, ny, ox, oy) * 2) + (resources and -nd * seek)
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: move deterministically toward corner opposite opponent
    cx = 0 if ox > w - 1 - ox else w - 1
    cy = 0 if oy > h - 1 - oy else h - 1
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        score = -cheb(nx, ny, cx, cy) * 10 - cheb(nx, ny, ox, oy)
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]