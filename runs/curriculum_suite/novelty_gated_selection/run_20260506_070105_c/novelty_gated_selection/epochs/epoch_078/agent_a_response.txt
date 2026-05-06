def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_dx, best_dy = 0, 0
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        local_best = -10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer targets we can beat (od - sd), but also avoid very long self paths.
            val = (od - sd) * 12 - sd
            # Mild anti-stall: prefer reducing distance to the "frontier" (closest resource overall).
            local_best = val if val > local_best else local_best

        # Also gently discourage moving closer to opponent when tie-breaking.
        opp_next = man(nx, ny, ox, oy)
        val2 = local_best * 100 - opp_next
        if val2 > best_val:
            best_val = val2
            best_dx, best_dy = dx, dy

    if best_dx > 1: best_dx = 1
    if best_dx < -1: best_dx = -1
    if best_dy > 1: best_dy = 1
    if best_dy < -1: best_dy = -1
    return [int(best_dx), int(best_dy)]