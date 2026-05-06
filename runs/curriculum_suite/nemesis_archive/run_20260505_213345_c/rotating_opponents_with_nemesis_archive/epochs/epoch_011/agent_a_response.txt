def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Sweep-row opponent: try to avoid moving into the opponent's current row band.
    row_pen = 6
    best_target = None
    best_tkey = None
    for rx, ry in resources:
        ds = dist2(sx, sy, rx, ry)
        dyrow = abs(ry - oy)
        # Prefer different row than opponent to deny sweep
        key = (ds + row_pen * (dyrow == 0) + (row_pen // 2) * (dyrow == 1), dist2(ox, oy, rx, ry), rx, ry)
        if best_tkey is None or key < best_tkey:
            best_tkey = key
            best_target = (rx, ry)

    tx, ty = best_target if best_target is not None else (sx, sy)

    # Choose best feasible immediate move toward the chosen target, with row avoidance.
    best_m = (0, 0)
    best_mscore = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            step = dist2(nx, ny, tx, ty)
            # Keep steering away from opponent row to stay off their sweep path
            steer = row_pen * (abs(ny - oy) == 0) + (row_pen // 2) * (abs(ny - oy) == 1)
            # Mild prefer diagonal/forward progress vs pure sideways stagnation
            progress = -abs(nx - sx) - abs(ny - sy) * 0.1
            mscore = step + steer + progress * 0.01
            if best_mscore is None or mscore < best_mscore or (mscore == best_mscore and (dx, dy) < best_m):
                best_mscore = mscore
                best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]