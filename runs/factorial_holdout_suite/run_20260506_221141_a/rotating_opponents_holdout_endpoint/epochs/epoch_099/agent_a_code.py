def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick a target we can reach sooner than opponent (or at least deny them strongly).
    best = None
    best_key = None
    for (tx, ty) in resources:
        sdist = cheb(sx, sy, tx, ty)
        odist = cheb(ox, oy, tx, ty)
        key = (odist - sdist, -sdist, -((tx + ty) & 1), -(tx * 31 + ty * 17))
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)
    tx, ty = best

    # Candidate moves (including stay), prefer those reducing our distance and increasing opponent distance.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        sd = cheb(nx, ny, tx, ty)
        od = cheb(nx, ny, ox, oy)
        oppd = cheb(ox, oy, tx, ty)
        # primary: get closer to target, secondary: make opponent farther from target
        mkey = (-sd, (oppd - sd), -od, (dx * 3 + dy))
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = [dx, dy]

    # If all candidate moves are blocked, stay put.
    return [int(best_move[0]), int(best_move[1])]