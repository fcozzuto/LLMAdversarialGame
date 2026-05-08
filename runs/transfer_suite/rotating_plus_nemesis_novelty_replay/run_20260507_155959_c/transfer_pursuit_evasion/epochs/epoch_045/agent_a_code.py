def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    res = observation.get("resources", None)
    resources = res if isinstance(res, list) else []
    if not resources:
        resources = []

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target = (ox, oy)
    if resources:
        best = None
        bs = 10**9
        for p in resources:
            px, py = int(p[0]), int(p[1])
            if not valid(px, py):
                continue
            d = abs(px - sx) + abs(py - sy)
            if d < bs:
                bs = d
                best = (px, py)
        if best is not None:
            target = best

    opp = (ox, oy)
    me = (sx, sy)
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        nme = (nx, ny)
        val = -dist(nme, target)
        val += 0.5 * dist(nme, opp)
        if resources and nme in set(tuple(p) for p in resources):
            val += 1000
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]