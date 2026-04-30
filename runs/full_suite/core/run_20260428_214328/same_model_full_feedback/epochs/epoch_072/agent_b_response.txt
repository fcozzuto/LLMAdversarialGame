def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # Move to increase distance from opponent while avoiding obstacles locally
        best = (-(10**9), 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = dist((nx, ny), (ox, oy))
            # tie-break: prefer upward/left for determinism
            v -= 0.001 * (nx * 2 + ny)
            if v > best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]]

    # Pick a resource we can reach sooner than the opponent; tie-break by distance and coords
    best_r = None
    best_key = None
    for r in resources:
        sd = dist((sx, sy), r)
        od = dist((ox, oy), r)
        lead = od - sd  # positive means we are closer
        key = (lead, -sd, -r[0], -r[1])  # deterministic
        if best_key is None or key > best_key:
            best_key = key
            best_r = r

    target = best_r
    # Local move choice: get closer to target, keep away from opponent, avoid stepping into dead-ends
    best = (-(10**9), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_t = dist((nx, ny), target)
        d_o = dist((nx, ny), (ox, oy))
        # discourage moving into areas with few valid neighbors
        neigh = 0
        for mdx, mdy in moves:
            tx, ty = nx + mdx, ny + mdy
            if valid(tx, ty):
                neigh += 1
        v = -d_t + 0.15 * d_o + 0.03 * neigh
        # tiny deterministic tie-break
        v -= 0.0001 * (nx - w // 2) * (nx - w // 2) + 0.0001 * (ny)
        if v > best[0]:
            best = (v, dx, dy)

    return [best[1], best[2]]