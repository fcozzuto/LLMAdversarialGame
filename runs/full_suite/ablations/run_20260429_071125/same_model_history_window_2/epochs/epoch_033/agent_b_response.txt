def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    cx, cy = (w - 1) // 2, (h - 1) // 2
    resources_left = observation.get("remaining_resource_count", None)
    try:
        resources_left = int(resources_left) if resources_left is not None else len(resources)
    except:
        resources_left = len(resources)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Defensive/offensive evaluation: pick resource we can beat opponent to; otherwise maximize safety.
        val = 0
        if resources:
            best_res = None
            best_gap = -10**18
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                gap = od - sd  # positive => we are closer now
                if gap > best_gap:
                    best_gap = gap
                    best_res = (rx, ry)
            rx, ry = best_res
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Encourage beating opponent, but avoid getting trapped far away when resources are low.
            val += 1000 * (best_gap > 0)
            val += 30 * best_gap
            val += -2 * sd
            # Small bias to not hand over the same target: if opponent also close, increase distance from their position.
            val += -3 * cheb(nx, ny, ox, oy)
        else:
            val += -cheb(nx, ny, ox, oy)
            val += -2 * cheb(nx, ny, cx, cy)

        # When few resources remain, prioritize ending near resources by reducing distance to center as fallback.
        if resources_left is not None and resources_left <= 4 and resources:
            val += -2 * cheb(nx, ny, cx, cy)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]