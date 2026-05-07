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

    if not resources or not legal:
        return [0, 0]

    best_r = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Prefer quick pickups; then deny (resource far from opponent).
        key = (sd, -od, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    best_m = (0, 0)
    best_mkey = None
    for dx, dy, nx, ny in legal:
        sd_next = dist(nx, ny, tx, ty)
        # Additional pressure: how fast we could reach any resource after this move.
        min_any = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            d = dist(nx, ny, rx, ry)
            if min_any is None or d < min_any:
                min_any = d
        od_target = dist(ox, oy, tx, ty)
        # Lexicographic tie-break favors staying/low deltas deterministically.
        mkey = (sd_next, -od_target, min_any, dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]