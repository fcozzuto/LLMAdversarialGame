def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (W - 1, H - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                blocked.add((x, y))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = observation.get("unclaimed_cells") or []
    best = None
    best_key = None
    for c in targets:
        if not c or len(c) < 2:
            continue
        tx, ty = int(c[0]), int(c[1])
        if not (0 <= tx < W and 0 <= ty < H) or (tx, ty) in blocked:
            continue
        d1 = dist((sx, sy), (tx, ty))
        d2 = dist((ox, oy), (tx, ty))
        key = (d2 - d1, d1, tx, ty)
        if best_key is None or key > best_key:
            best_key, best = key, (tx, ty)

    if best is None:
        best = (ox, oy)

    best_move = (0, 0)
    best_move_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < W and 0 <= ny < H):
                continue
            if (nx, ny) in blocked:
                continue
            v1 = dist((nx, ny), best)
            v2 = dist((ox, oy), best)
            val = (v2 - v1, -v1, dx, dy)
            if best_move_val is None or val > best_move_val:
                best_move_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]