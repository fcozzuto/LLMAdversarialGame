def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((p[0], p[1]))

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # deterministic fallback: move toward opponent's side to deny
        tx = 0 if sx > (w - 1) / 2 else (w - 1)
        ty = 0 if sy > (h - 1) / 2 else (h - 1)
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = dist8(nx, ny, tx, ty) * -1
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    my_center = abs((w - 1) / 2 - sx) + abs((h - 1) / 2 - sy)
    best_target = None
    best_val = -10**18

    for rx, ry in resources:
        if not ok(rx, ry):
            continue
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        adv = op_d - my_d  # positive if I'm closer
        v = adv * 1500 - my_d * 7 - my_center * 0.1 - (rx + ry) * 0.00001
        if v > best_val:
            best_val = v
            best_target = (rx, ry)

    # If all resources are on obstacles, just avoid obstacles and drift to farthest corner deterministically
    if best_target is None:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda p: dist8(sx, sy, p[0], p[1]))
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                v = -dist8(nx, ny, tx, ty)
                if v > bestv or (v == bestv and (dx, dy) < best):
                    bestv = v
                    best = (dx, dy)
        return [best[0], best[1]]

    rx, ry = best_target
    # Greedy one-step: maximize (opportunity of securing target) with obstacle-safe moves
    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_d2 = dist8(nx, ny, rx, ry)
        op_d2 = dist8(ox, oy, rx, ry)
        adv2 = op_d2 - my_d2
        v = adv2 * 1500 - my_d2 * 8 - (dx == 0 and dy == 0) * 3
        # tiny deterministic tie-break
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]