def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        tx, ty = min(resources, key=lambda r: dist((sx, sy), r))
        oppd = dist((ox, oy), (tx, ty))
        best = None
        bestv = -10**18
        for mdx, mdy in moves:
            nx, ny = sx + mdx, sy + mdy
            if not valid(nx, ny):
                continue
            myd = dist((nx, ny), (tx, ty))
            oppgain = 0
            if myd <= oppd:
                oppgain = 1
            v = (-myd) + 0.1 * dist((nx, ny), (ox, oy)) + 0.3 * oppgain
            if v > bestv or (v == bestv and (mdx, mdy) < best):
                bestv = v
                best = (mdx, mdy)
        return list(best) if best is not None else [0, 0]
    else:
        tx = 0 if sx >= w - 1 - sx else w - 1
        ty = 0 if sy >= h - 1 - sy else h - 1
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        for mdx, mdy in moves:
            nx, ny = sx + mdx, sy + mdy
            if valid(nx, ny):
                return [mdx, mdy]
        return [0, 0]