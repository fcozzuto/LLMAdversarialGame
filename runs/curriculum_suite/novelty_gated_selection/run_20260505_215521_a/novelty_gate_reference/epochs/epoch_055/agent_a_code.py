def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist(x, y, tx, ty):
        dx = x - tx
        if dx < 0: dx = -dx
        dy = y - ty
        if dy < 0: dy = -dy
        return dx + dy

    target = None
    if resources:
        target = resources[0]
        best = 10**9
        for r in resources:
            v = dist(sx, sy, r[0], r[1])
            if v < best or (v == best and (r[0], r[1]) < (target[0], target[1])):
                best = v
                target = r

    if target is None:
        target = (ox, oy)

    tx, ty = int(target[0]), int(target[1])

    bestm = (0, 0)
    bestv = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = dist(nx, ny, tx, ty)
        if v < bestv:
            bestv = v
            bestm = (dx, dy)
        elif v == bestv:
            if (dx, dy) < bestm:
                bestm = (dx, dy)
    nx, ny = sx + bestm[0], sy + bestm[1]
    if ok(nx, ny):
        return [bestm[0], bestm[1]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            return [dx, dy]
    return [0, 0]