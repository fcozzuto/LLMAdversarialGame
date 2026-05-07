def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    if not resources:
        return [0, 0]
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    tr = int(observation.get("turns_remaining", 0))
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        # Prefer guaranteed race wins; else pick a contestable resource that still improves position.
        # Also bias toward our side relative to opponent to reduce denial effectiveness.
        side = (rx + ry) - (ox + oy)
        center_bias = -((rx - cx) * (rx - cx) + (ry - cy) * (ry - cy))
        key = (adv >= 0, adv, -sd, side, center_bias, -((sd + od) % 3), -tr)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Choose move that maximizes post-move advantage while still getting close to target.
    bestm = None
    bestm_key = None
    for dx, dy, nx, ny in legal:
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        adv2 = od2 - sd2
        reach = -sd2
        # If we are already on target, stay if legal (deterministic).
        on = 1 if (nx == tx and ny == ty) else 0
        key = (on, adv2 >= 0, adv2, reach, -abs(nx - tx) - abs(ny - ty), -dx, -dy)
        if bestm_key is None or key > bestm_key:
            bestm_key = key
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]