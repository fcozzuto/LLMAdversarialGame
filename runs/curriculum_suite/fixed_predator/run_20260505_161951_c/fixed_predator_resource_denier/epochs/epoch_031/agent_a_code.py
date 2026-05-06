def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target():
        best = None
        bestv = -10**18
        for rx, ry in resources:
            sd = cheb(rx, ry, x, y)
            od = cheb(rx, ry, ox, oy)
            # prefer resources we're significantly closer to; tie-break toward faster + higher positional pressure
            v = (od - sd) * 1000 - sd * 3 - (abs(rx - (w // 2)) + abs(ry - (h // 2)))
            if v > bestv:
                bestv = v
                best = (rx, ry)
        return best

    if resources:
        tx, ty = best_target()
        bestm = [0, 0]
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            sd = cheb(nx, ny, tx, ty)
            od = cheb(nx, ny, ox, oy)
            # move that improves our approach; also keep distance from opponent to reduce contest success
            v = -sd * 10 + od - (dx == 0 and dy == 0) * 0.1
            if v > bestv:
                bestv = v
                bestm = [dx, dy]
        return bestm

    # No resources visible: drift toward center while keeping away from opponent, avoiding obstacles.
    cx, cy = w // 2, h // 2
    bestm = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        v = -(cheb(nx, ny, cx, cy)) * 5 - cheb(nx, ny, ox, oy)
        if v > bestv:
            bestv = v
            bestm = [dx, dy]
    return bestm