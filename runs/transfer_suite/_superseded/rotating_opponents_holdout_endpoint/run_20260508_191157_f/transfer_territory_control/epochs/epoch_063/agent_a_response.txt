def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    cx, cy = w // 2, h // 2
    unclaimed = observation.get("unclaimed_cells") or []
    if not unclaimed:
        unclaimed = observation.get("resources") or []
    targets = []
    for p in unclaimed:
        if not p or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            targets.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not targets:
        # Fallback: drift toward farthest corner from opponent
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda t: (t[0] - ox) * (t[0] - ox) + (t[1] - oy) * (t[1] - oy))
        best_dir = (0, 0)
        best_d = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not cell_ok(nx, ny):
                continue
            d = abs(nx - tx) + abs(ny - ty)
            if d < best_d or (d == best_d and (dx, dy) < best_dir):
                best_d, best_dir = d, (dx, dy)
        return [best_dir[0], best_dir[1]]

    # Choose target: maximize distance from opponent, mildly prefer toward center and prefer proximity to self.
    best_t = targets[0]
    best_key = None
    for x, y in targets:
        d_opp = (x - ox) * (x - ox) + (y - oy) * (y - oy)
        d_ctr = (x - cx) * (x - cx) + (y - cy) * (y - cy)
        d_self = (x - sx) * (x - sx) + (y - sy) * (y - sy)
        # score: far from opponent, not too far from center, not too far from us
        key = (d_opp, -d_ctr * 0.25, -d_self)
        if best_key is None or key > best_key or (key == best_key and (x, y) < best_t):
            best_key = key
            best_t = (x, y)

    tx, ty = best_t
    # Move one step to reduce Manhattan distance to target, tie-break toward increasing distance from opponent.
    best_dir = (0, 0)
    best_dist = 10**9
    best_dopp = -1
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        dopp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if dist < best_dist or (dist == best_dist and (dopp > best_dopp or (dopp == best_dopp and (dx, dy) < best_dir))):
            best_dist, best_dopp, best_dir = dist, dopp, (dx, dy)

    return [int(best_dir[0]), int(best_dir[1])]