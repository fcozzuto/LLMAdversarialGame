def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obs

    target = None
    bestv = -10**18
    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer places we are closer to than opponent; strongly discourage giving them the race.
        v = (do - ds) * 12 - ds
        if do <= ds:
            v -= 25
        if v > bestv:
            bestv = v
            target = (rx, ry)

    if target is None:
        # No valid resources: drift toward center while avoiding obstacles.
        cx, cy = (W - 1) // 2, (H - 1) // 2
        target = (cx, cy)

    tx, ty = target
    do = cheb(ox, oy, tx, ty)

    bestmove = (0, 0)
    bestscore = -10**18
    # Deterministic tie-break: fixed move order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds = cheb(nx, ny, tx, ty)
        score = (do - ds) * 12 - ds
        # If scores tie, prefer moves that reduce distance (and then prefer earlier in order).
        if score > bestscore:
            bestscore = score
            bestmove = (dx, dy)

    return [int(bestmove[0]), int(bestmove[1])]