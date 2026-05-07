def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    if not resources:
        return [0, 0]

    def time_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def best_key_from(posx, posy):
        px = int(posx)
        py = int(posy)
        bestk = None
        for p in resources:
            tx, ty = int(p[0]), int(p[1])
            if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obs:
                continue
            ds = time_cheb(px, py, tx, ty)
            do = time_cheb(ox, oy, tx, ty)
            # Maximize advantage (opponent later), then minimize our time, then prefer checkerboard parity to keep routes stable.
            key = (do - ds, -ds, -((tx + ty) & 1), -(tx + ty))
            if bestk is None or key > bestk:
                bestk = key
        return bestk if bestk is not None else (-(10**9), 0, 0, 0)

    # Prefer moves that improve our best achievable advantage in 1-step lookahead.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = [0, 0]
    bestv = None
    base = best_key_from(sx, sy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        k = best_key_from(nx, ny)
        # Tie-break: keep closer to current best target tendency via immediate improvement in the same key's first component.
        v = (k[0] - base[0], k[0], k[1], k[2], k[3])
        if bestv is None or v > bestv:
            bestv = v
            bestm = [dx, dy]

    # If all candidate moves filtered (surrounded by obstacles/out of bounds), fall back to staying still.
    if bestv is None:
        return [0, 0]
    return bestm