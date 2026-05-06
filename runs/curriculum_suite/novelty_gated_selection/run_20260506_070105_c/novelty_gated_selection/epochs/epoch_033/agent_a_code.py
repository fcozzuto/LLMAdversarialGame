def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        try:
            obs.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Target: nearest resource; deterministic tie-break by (y, x)
    best_r = None
    best_d = 10**9
    for r in resources:
        try:
            rx, ry = int(r[0]), int(r[1])
        except Exception:
            continue
        if not inb(rx, ry):
            continue
        d = man(sx, sy, rx, ry)
        if d < best_d or (d == best_d and (ry, rx) < (best_r[1], best_r[0])):
            best_d = d
            best_r = (rx, ry)

    if best_r is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_r

    # Evaluate moves: maximize progress to target, stay away from opponent, avoid obstacles.
    best_score = -10**18
    best_move = (0, 0)
    cur_dt = man(sx, sy, tx, ty)
    cur_do = man(sx, sy, ox, oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dt = man(nx, ny, tx, ty)
        do = man(nx, ny, ox, oy)

        # Prefer strictly improving distance; otherwise keep moving.
        progress = cur_dt - dt
        score = 1000 * progress

        # Keep away from opponent, especially if we're not improving.
        score += 5 * (do - cur_do)

        # Mild center bias to reduce corner trapping once resources are gone.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score += -0.01 * (abs(nx - cx) + abs(ny - cy))

        # Deterministic tie-break: smaller (dx,dy) preference order.
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]