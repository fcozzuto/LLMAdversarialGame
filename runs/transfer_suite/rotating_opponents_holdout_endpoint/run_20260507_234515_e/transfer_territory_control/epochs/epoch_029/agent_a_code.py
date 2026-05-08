def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    resources = []
    for p in (observation.get("resources") or []):
        try:
            resources.append((int(p[0]), int(p[1])))
        except:
            pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        ax, ay = a
        bx, by = b
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        if resources:
            dres = min(dist((nx, ny), r) for r in resources)
        else:
            dres = 10**9

        dop = dist((nx, ny), (ox, oy))
        adv = dop
        key = (0 if resources else 1, dres, -adv, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]