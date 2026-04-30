def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = [0, 0]
    best_val = -10**18

    # If no resources, just drift to center while avoiding obstacles
    if not resources:
        target_x, target_y = int(round(cx)), int(round(cy))
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            val = -cheb(nx, ny, target_x, target_y)
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
        return best_move

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Prefer capturing resources we are closer to than opponent, and that are close to us.
        best_resource_val = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Higher when we beat opponent (od - sd), and when sd is small.
            val = (od - sd) * 3 - sd
            # Extra push if we land on resource.
            if sd == 0:
                val += 1000
            if val > best_resource_val:
                best_resource_val = val

        # Safety/spacing: discourage moving too close to opponent unless it helps capturing.
        spacing = cheb(nx, ny, ox, oy)
        danger = 0
        if spacing <= 1:
            danger = 15
        elif spacing <= 2:
            danger = 6

        # Small preference for general progress (closer to center if ties)
        center_bias = -cheb(nx, ny, int(round(cx)), int(round(cy))) * 0.05

        total = best_resource_val - danger + center_bias
        if total > best_val:
            best_val = total
            best_move = [dx, dy]

    return best_move