def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    legal = []
    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not legal or not resources:
        return [0, 0]

    # Precompute resource info
    res = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        res.append((rx, ry, sd, od))

    def best_from(nx, ny):
        best = None
        for rx, ry, _, od in res:
            nsd = dist(nx, ny, rx, ry)
            # Strong priority: resources we can arrive earlier; then deny by increasing opponent advantage.
            key = (nsd, od - nsd, -(rx + ry), -rx, -ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        return best[0]

    # Evaluate each move by resulting state's best attainable advantage
    best_move = None
    best_key = None
    for dx, dy, nx, ny in legal:
        key = best_from(nx, ny)
        # Tie-break: prefer moves that don't drift away from current good resources
        # (and deterministic order to avoid oscillations).
        drift = abs(nx - sx) + abs(ny - sy)
        key2 = (key, drift, dx, dy)
        if best_key is None or key2 < best_key:
            best_key = key2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]