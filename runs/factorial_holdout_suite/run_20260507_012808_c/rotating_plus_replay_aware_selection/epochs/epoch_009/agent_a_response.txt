def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        tx, ty = w - 1 - sx, h - 1 - sy
        best_move = (10**9, 10**9)
        best = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d1 = dist((nx, ny), (tx, ty))
            d2 = -dist((nx, ny), (ox, oy))
            cand = (d1, d2)
            if cand < best_move:
                best_move = cand
                best = [dx, dy]
        return best

    best_target = None
    best_key = None
    for rx, ry in resources:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Prefer contested resources where we are not farther; break ties by closeness.
        key = (1 if sd <= od else 0, od - sd, -sd)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sd_next = dist((nx, ny), (tx, ty))
        # After moving, prefer decreasing our distance; also prefer increasing our lead.
        lead_next = dist((ox, oy), (tx, ty)) - sd_next
        val = (sd_next, -lead_next, abs(nx - tx) + abs(ny - ty))
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)
    return [int(best[0]), int(best[1])]