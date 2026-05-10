def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or ("escape" in role)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = moves[4]
    best_val = None

    def neighbor_block_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
                c += 1
        return c

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)
        dist_to_center = abs(nx - cx) + abs(ny - cy)
        nb = neighbor_block_count(nx, ny)

        if is_evader:
            # Run away, but avoid getting surrounded and avoid drifting too hard into dead-end corners.
            val = (d * 10.0) - (nb * 1.2) - (dist_to_center * 0.02)
        else:
            # Pursue: minimize distance, avoid moves that put us near obstacles (reduce being forced into corners).
            val = (-d * 10.0) - (nb * 0.8) - (dist_to_center * 0.01)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move