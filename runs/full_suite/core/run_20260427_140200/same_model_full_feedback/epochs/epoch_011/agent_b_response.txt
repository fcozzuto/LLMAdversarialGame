def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = w // 2, h // 2

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    if resources:
        best_t = None
        best_key = None
        for tx, ty in resources:
            sd = dist(sx, sy, tx, ty)
            od = dist(ox, oy, tx, ty)
            # Prefer targets we are significantly closer to; tie-break by closeness to self, then coordinates.
            key = (0 if sd <= od else 1, sd - od, sd, tx, ty)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        tx, ty = cx, cy

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dself = dist(nx, ny, tx, ty)
        dopp = dist(nx, ny, ox, oy)
        dcenter = abs(nx - cx) + abs(ny - cy)
        # Maximize: move closer to target; keep some distance from opponent; mild center bias.
        val = (-dself) + (dopp // 2) - dcenter // 3
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]