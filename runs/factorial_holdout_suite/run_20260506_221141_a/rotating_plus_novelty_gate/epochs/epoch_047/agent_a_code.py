def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not resources:
        return [0, 0]
    if (sx, sy) in set(resources):
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def king_dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny = sx, sy
        # prefer moves that let us beat opponent on a resource soonest
        local_best = -10**9
        for rx, ry in resources:
            self_t = king_dist(nx, ny, rx, ry)
            opp_t = king_dist(ox, oy, rx, ry)
            # strong advantage for being earlier; tie-break on closeness to resource and on reducing opp lead
            val = (opp_t - self_t) * 10 - self_t
            if (rx, ry) == (nx, ny):
                val += 1000
            # small penalty for moving further from current best resource direction (deterministic stabilizer)
            local_best = val if val > local_best else local_best
        # obstacle-aware tie-break: avoid being adjacent to obstacles if not required
        adj_pen = 0
        if (nx, ny) != (sx, sy):
            for ax, ay in ((nx+1, ny), (nx-1, ny), (nx, ny+1), (nx, ny-1)):
                if (ax, ay) in blocked:
                    adj_pen -= 1
        val2 = local_best + adj_pen
        if best is None or val2 > best:
            best = val2
            best_move = [nx - sx, ny - sy]
    if best_move[0] not in (-1, 0, 1) or best_move[1] not in (-1, 0, 1):
        return [0, 0]
    return best_move