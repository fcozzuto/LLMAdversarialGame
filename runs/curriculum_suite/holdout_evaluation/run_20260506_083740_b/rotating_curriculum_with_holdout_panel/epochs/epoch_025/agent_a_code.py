def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    resources = observation.get("resources", []) or []

    if resources:
        best = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = r[0], r[1]
            d = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(ry - oy)
            score = d - 0.4 * do
            if best is None or score < best[0]:
                best = (score, rx, ry)
        _, tx, ty = best

        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)

        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]

        for mdx, mdy in moves:
            nx, ny = sx + mdx, sy + mdy
            if valid(nx, ny) and (abs(tx - nx) + abs(ty - ny) <= abs(tx - sx) + abs(ty - sy)):
                return [mdx, mdy]
        for mdx, mdy in moves:
            nx, ny = sx + mdx, sy + mdy
            if valid(nx, ny):
                return [mdx, mdy]
        return [0, 0]

    tx, ty = 0, 0
    if sx <= w - 1 - sx:
        tx = w - 1 if sx == 0 else 0
    else:
        tx = 0 if sx == w - 1 else w - 1
    if sy <= h - 1 - sy:
        ty = h - 1 if sy == 0 else 0
    else:
        ty = 0 if sy == h - 1 else h - 1

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