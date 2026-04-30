def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                resources.append((x, y))

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    def score(nx, ny):
        if resources:
            bestd = 10**9
            for rx, ry in resources:
                d = abs(nx - rx) + abs(ny - ry)
                if d < bestd:
                    bestd = d
            # Prefer approaching resources; slight preference for staying away from opponent
            return bestd + 0.01 * (abs(nx - ox) + abs(ny - oy))
        # No visible resources: move toward center, also avoid opponent a bit
        cx, cy = (W - 1) // 2, (H - 1) // 2
        return abs(nx - cx) + abs(ny - cy) + 0.01 * (abs(nx - ox) + abs(ny - oy))

    best_move = (0, 0)
    best_sc = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            sc = score(nx, ny)
            if sc < best_sc or (sc == best_sc and (dx, dy) < best_move):
                best_sc = sc
                best_move = (dx, dy)
    return [best_move[0], best_move[1]]