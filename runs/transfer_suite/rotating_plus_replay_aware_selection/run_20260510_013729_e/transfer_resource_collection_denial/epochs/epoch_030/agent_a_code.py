def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w, h = observation.get("grid_width", 1), observation.get("grid_height", 1)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    ob = set()
    for p in obstacles:
        try:
            x, y = p
            ob.add((x, y))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for r in resources:
        try:
            rx, ry = r
        except Exception:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer targets where we are closer (do - ds larger), then closer (ds smaller)
        key = (do - ds, -ds, -(rx * 1000003 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best if best is not None else (sx, sy)

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    chosen = (0, 0)
    chosen_key = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in ob:
            continue
        ds_next = cheb(nx, ny, tx, ty)
        do_next = cheb(ox, oy, tx, ty)
        # Prefer decreasing our distance while keeping advantage over opponent
        key = (do_next - ds_next, -ds_next, -((dx + 1) * 9 + (dy + 1)))
        if chosen_key is None or key > chosen_key:
            chosen_key = key
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]