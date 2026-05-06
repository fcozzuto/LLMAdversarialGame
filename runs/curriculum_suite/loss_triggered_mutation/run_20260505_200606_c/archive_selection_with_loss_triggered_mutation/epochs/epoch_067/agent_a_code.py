def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_resource(mx, my):
        if not resources:
            return None
        best_r = None
        best_v = None
        for rx, ry in resources:
            md = man(mx, my, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources we can reach earlier; break ties by moving closer,
            # then by being farther from opponent.
            v = (od - md) * 100 - md * 2 + (md == od) * 1 - (od - md == 0) * 0
            if best_v is None or v > best_v or (v == best_v and (rx, ry) < best_r):
                best_v = v
                best_r = (rx, ry)
        return best_r

    # If no resources, drift toward center while keeping distance from opponent.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = man(nx, ny, ox, oy) * 3 - man(nx, ny, cx, cy)
            if bestv is None or v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    target = best_resource(sx, sy)
    if target is None:
        return [0, 0]
    tx, ty = target

    # If we're already on a resource cell, move to improve immediate tempo.
    best_move = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        md = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        # Strongly prefer decreasing our distance to the chosen target,
        # but also keep competitive advantage if another resource becomes better.
        v = (od - md) * 120 - md * 3 + (md == 0) * 50
        if bestv is None or v > bestv or (v == bestv and (dx, dy) < best_move):
            bestv = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]