def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    best_val = -10**30
    best_target = resources[0]
    for rx, ry in resources:
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        val = (opd - myd) * 1000 - myd
        if val > best_val or (val == best_val and (rx, ry) < best_target):
            best_val = val
            best_target = (rx, ry)

    rx, ry = best_target
    best_next = (sx, sy)
    best_next_val = -10**30
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd = manh(nx, ny, rx, ry)
        opd = manh(ox, oy, rx, ry)
        val = (opd - myd) * 1000 - myd
        if val > best_next_val or (val == best_next_val and (nx, ny) < best_next):
            best_next_val = val
            best_next = (nx, ny)

    return [best_next[0] - sx, best_next[1] - sy]