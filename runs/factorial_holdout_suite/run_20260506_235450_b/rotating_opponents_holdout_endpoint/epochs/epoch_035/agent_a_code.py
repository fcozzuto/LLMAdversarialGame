def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, dict) and "x" in a and "y" in a:
            x, y = int(a["x"]), int(a["y"])
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        return max(abs(ax - bx), abs(ay - by))

    def resource_score(cell, tx, ty):
        myd = cheb(cell[0], cell[1], tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Prefer cells that can reach resources where we are earlier; tie-break by speed.
        return (myd - opd, myd, abs(tx - ox) + abs(ty - oy), tx, ty)

    # Choose target resource we can reach earlier (or at least fastest).
    best_t = None
    best_s = None
    for tx, ty in resources:
        s = resource_score((sx, sy), tx, ty)
        if best_s is None or s < best_s:
            best_s = s
            best_t = (tx, ty)

    tx, ty = best_t

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_m = (0, 0)
    best_ms = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        # If opponent is close to the target, try to minimize distance to it.
        ms = (cheb(nx, ny, tx, ty), cheb(ox, oy, tx, ty), (nx - sx, ny - sy))
        if best_ms is None or ms < best_ms:
            best_ms = ms
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]