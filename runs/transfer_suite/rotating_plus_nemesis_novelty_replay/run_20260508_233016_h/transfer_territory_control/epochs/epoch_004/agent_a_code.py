def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    unclaimed = observation.get("unclaimed_cells") or []
    self_terr = observation.get("self_territory") or []
    obstacles = observation.get("obstacles") or []

    if not unclaimed and not self_terr:
        return [0, 0]

    obst = set((int(px), int(py)) for px, py in obstacles)
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        return d + (e if e >= 0 else -e)

    targets = []
    sset = set((int(px), int(py)) for px, py in self_terr)
    if sset:
        u = set((int(px), int(py)) for px, py in unclaimed)
        for sx, sy in sset:
            for dx, dy in dirs:
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in u:
                    targets.append((nx, ny))
    if not targets:
        targets = [(int(px), int(py)) for px, py in unclaimed]

    if not targets:
        return [0, 0]

    best_t = targets[0]
    best_key = (dist(x, y, best_t[0], best_t[1]), -dist(best_t[0], best_t[1], ox, oy))
    for tx, ty in targets[1:]:
        key = (dist(x, y, tx, ty), -dist(tx, ty, ox, oy))
        if key < best_key:
            best_key, best_t = key, (tx, ty)

    tx, ty = best_t
    best_m = (0, 0)
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue
        s = -dist(nx, ny, tx, ty) + dist(nx, ny, ox, oy) // 2
        if s > best_s or (s == best_s and (dx, dy) < best_m):
            best_s, best_m = s, (dx, dy)

    return [int(best_m[0]), int(best_m[1])]