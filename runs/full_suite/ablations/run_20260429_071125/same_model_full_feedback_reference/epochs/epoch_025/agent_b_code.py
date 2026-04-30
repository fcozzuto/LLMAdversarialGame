def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))
    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles:
        return [0, 0]
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    opp_pos = (ox, oy)
    best_step = (0, 0)
    best_val = -10**18

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            v = -cheb(nx, ny, tx, ty)
            if v > best_val:
                best_val = v
                best_step = (dx, dy)
        return [best_step[0], best_step[1]]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        md = 10**9
        rel = -10**9
        for rx, ry in resources:
            dmy = cheb(nx, ny, rx, ry)
            dop = cheb(opp_pos[0], opp_pos[1], rx, ry)
            # Prefer resources where we are closer than opponent; break ties by absolute closeness.
            v = (dop - dmy)
            if v > rel:
                rel = v
                md = dmy
        # Mild tie-break: prefer slightly smaller distance for the best relative target.
        val = rel * 1000 - md
        if val > best_val:
            best_val = val
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]