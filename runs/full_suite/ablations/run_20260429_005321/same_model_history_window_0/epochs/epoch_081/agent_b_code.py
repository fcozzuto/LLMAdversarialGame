def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = []
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))

    if not valid:
        return [0, 0]

    if resources:
        best = None
        for rx, ry in resources:
            ud = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            val = ud - 0.5 * od
            if best is None or val < best[0] or (val == best[0] and (ud, od) < best[1]):
                best = (val, (ud, od), (rx, ry))
        tx, ty = best[2]
    else:
        # No resources: move to maximize distance from opponent
        tx, ty = ox, oy

    def neighbor_score(dx, dy, nx, ny):
        if resources:
            ud = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Prefer reducing our distance, and slightly worsening opponent relative prospects
            return (ud, od - ud)
        else:
            # Maximize distance from opponent
            return (-cheb(nx, ny, tx, ty), 0)

    chosen = None
    for dx, dy, nx, ny in valid:
        sc = neighbor_score(dx, dy, nx, ny)
        if chosen is None or sc < chosen[0]:
            chosen = (sc, dx, dy)

    return [chosen[1], chosen[2]]