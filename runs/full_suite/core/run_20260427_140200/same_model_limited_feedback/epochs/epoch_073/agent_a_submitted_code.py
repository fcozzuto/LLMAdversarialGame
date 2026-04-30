def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', []) or []
    obstacles = observation.get('obstacles', []) or []
    obs = set(obstacles)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cd(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]

    if resources:
        best = None
        bestk = None
        for rx, ry in resources:
            ds = cd(sx, sy, rx, ry)
            do = cd(ox, oy, rx, ry)
            k = (do - ds, -ds, -rx, -ry)
            if bestk is None or k > bestk:
                bestk = k
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = ox, oy

    bestm = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        ds = cd(nx, ny, tx, ty)
        do = cd(ox, oy, tx, ty)
        adv = do - ds
        v = (adv, -ds, -abs(nx - ox) - abs(ny - oy), dx, dy)
        if bestv is None or v > bestv:
            bestv = v
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]