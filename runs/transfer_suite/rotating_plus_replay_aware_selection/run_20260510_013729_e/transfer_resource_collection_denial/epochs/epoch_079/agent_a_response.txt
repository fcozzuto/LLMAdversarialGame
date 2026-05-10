def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in obstacles}
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obst

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def nearest_resource_from(xy):
        if not resources:
            return None
        best = resources[0]
        bestd = dist(xy, best)
        for r in resources[1:]:
            d = dist(xy, r)
            if d < bestd:
                bestd = d
                best = r
        return best

    def opponent_next():
        if not resources:
            return (ox, oy)
        target = nearest_resource_from((ox, oy))
        best = (ox, oy, 10**9)
        for mdx, mdy in moves:
            nx, ny = ox + mdx, oy + mdy
            if not legal(nx, ny):
                continue
            d = dist((nx, ny), target)
            if d < best[2]:
                best = (nx, ny, d)
        return (best[0], best[1])

    if not resources:
        return [0, 0]

    oppn = opponent_next()
    best_move = (0, 0, (10**9, 10**9))
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not legal(nx, ny):
            continue
        best_r = (10**9, 10**9)
        for r in resources:
            sd = dist((nx, ny), r)
            od = dist(oppn, r)
            t = (sd - od, sd)
            if t < best_r:
                best_r = t
        if best_r < best_move[2]:
            best_move = (mdx, mdy, best_r)

    return [int(best_move[0]), int(best_move[1])]