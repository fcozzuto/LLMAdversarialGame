def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Pick target: maximize how much sooner we can reach than opponent; tie-break on closer to us, then coordinates.
    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        key = (do - ds, -ds, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    valid_moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid_moves.append((dx, dy, nx, ny))
    if not valid_moves:
        return [0, 0]

    # Prefer move that improves our relative progress to the selected target; if tie, reduce distance; if still tie, keep away from opponent.
    best_m = None
    best_m_key = None
    for dx, dy, nx, ny in valid_moves:
        ds = man(nx, ny, tx, ty)
        do = man(ox, oy, tx, ty)
        # Relative advantage after move (smaller ds better); also encourage moving closer to some other resource quickly.
        best_other = None
        for rx, ry in resources:
            if rx == tx and ry == ty:
                continue
            dso = man(nx, ny, rx, ry)
            if best_other is None or dso < best_other:
                best_other = dso
        if best_other is None:
            best_other = 10**9
        key = (-ds + (do - ds), -ds, best_other, man(nx, ny, ox, oy), dx, dy)
        if best_m_key is None or key > best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]