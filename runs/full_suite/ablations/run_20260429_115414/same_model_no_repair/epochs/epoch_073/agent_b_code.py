def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def passable(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def obst_dist(x, y):
        if not obstacles:
            return 99
        best = 10**9
        for px, py in obstacles:
            d = cheb(x, y, px, py)
            if d < best:
                best = d
        return best

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        best = (-10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not passable(nx, ny):
                continue
            score = -cheb(nx, ny, tx, ty) - 0.8 * (0 if obst_dist(nx, ny) > 1 else 2)
            if score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not passable(nx, ny):
            continue

        # Pick the resource that gives the biggest advantage from the candidate next cell
        chosen = None
        chosen_gap = -10**18
        chosen_selfd = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            gap = do - ds  # positive means next cell is closer than opponent
            if gap > chosen_gap or (gap == chosen_gap and ds < chosen_selfd):
                chosen_gap = gap
                chosen_selfd = ds
                chosen = (rx, ry)

        rx, ry = chosen
        ds = cheb(nx, ny, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if (nx, ny) == (rx, ry):
            on_resource = 2
        else:
            on_resource = 0

        od = obst_dist(nx, ny)
        obstacle_pen = 0.0 if od > 1 else (2.0 if od == 1 else 4.0)

        # Favor large immediate gap, also slightly prefer reducing self distance
        score = (do - ds) * 2.0 - ds * 0.15 + on_resource - obstacle_pen * 0.6
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]