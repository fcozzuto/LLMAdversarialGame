def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    def mdist(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    best_move = (0, 0)
    best_score = -10**18

    has_res = bool(resources)
    prev_res = 0
    if has_res:
        prev_res = min(mdist(sx, sy, rx, ry) for rx, ry in resources)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        score = 0
        if has_res:
            cur_res = min(mdist(nx, ny, rx, ry) for rx, ry in resources)
            score += (prev_res - cur_res) * 10
            if cur_res == 0:
                score += 50
        else:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score += -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))

        score += (mdist(nx, ny, ox, oy) * -1) * 1.5
        if dx == 0 and dy == 0:
            score -= 0.1

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]