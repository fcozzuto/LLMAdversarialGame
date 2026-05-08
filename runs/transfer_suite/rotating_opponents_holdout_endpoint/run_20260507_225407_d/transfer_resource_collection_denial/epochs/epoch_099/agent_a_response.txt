def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def kingdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Aggressive contesting: favor cells we can reach quickly and where opponent is slow.
    # Also prefer cells that are "off" opponent's likely sweep direction (change in y).
    best = None
    best_key = None
    for rx, ry in resources:
        d_me = kingdist(sx, sy, rx, ry)
        d_op = kingdist(ox, oy, rx, ry)
        # sweep_rows often advances along rows; bias against targets close in row to opponent
        row_bias = abs(ry - oy)
        key = (2 * d_me - d_op, d_me, -row_bias, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    primary = [(0, 0)]
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    primary = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (-dx, 0), (0, -dy), (0, 0)]

    candidates = []
    for mx, my in primary:
        nx, ny = sx + mx, sy + my
        if inb(nx, ny) and (nx, ny) not in obstacles:
            # Prefer moves that reduce king distance to target, then increase distance to opponent.
            k = (kingdist(nx, ny, tx, ty), -kingdist(nx, ny, ox, oy), abs(mx) + abs(my), mx, my)
            candidates.append((k, [mx, my]))
    candidates.sort(key=lambda t: t[0])
    return candidates[0][1] if candidates else [0, 0]