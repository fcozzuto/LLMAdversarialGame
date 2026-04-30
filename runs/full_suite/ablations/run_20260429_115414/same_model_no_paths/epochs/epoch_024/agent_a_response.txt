def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        # deterministic fallback: go toward opponent
        tx = ox - sx
        ty = oy - sy
        dx = 0 if tx == 0 else (1 if tx > 0 else -1)
        dy = 0 if ty == 0 else (1 if ty > 0 else -1)
        if valid(sx + dx, sy + dy):
            return [dx, dy]
        # try axis-aligned alternatives
        for ddx, ddy in [(dx, 0), (0, dy), (0, 0)]:
            if valid(sx + ddx, sy + ddy):
                return [ddx, ddy]
        return [0, 0]

    # Score moves by relative advantage on the best contested resource
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Find resource giving maximum relative advantage from this candidate
        local_best = -10**18
        for rx, ry in resources:
            d_us = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            # Encourage taking resources where we're ahead; also slightly discourage being too close to opponent
            rel = (d_op - d_us) * 10 - d_us
            if rel > local_best:
                local_best = rel

        # Extra tie-break: avoid stepping adjacent to obstacles if possible
        adj_pen = 0
        for bx, by in obstacles:
            if man(nx, ny, bx, by) <= 1:
                adj_pen += 2
        score = local_best - adj_pen

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move