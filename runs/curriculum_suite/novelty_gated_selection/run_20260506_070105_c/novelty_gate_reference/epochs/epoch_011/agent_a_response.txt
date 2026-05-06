def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            if inb(r[0], r[1]):
                res.append((r[0], r[1]))

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not res:
        cx, cy = w // 2, h // 2
        tx, ty = cx - sx, cy - sy
        dx = 0 if tx == 0 else (1 if tx > 0 else -1)
        dy = 0 if ty == 0 else (1 if ty > 0 else -1)
        return [dx, dy]

    # Immediate capture
    resset = set(res)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in resset:
            return [dx, dy]

    cx, cy = w // 2, h // 2
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Choose the resource that maximizes our "win margin" this turn.
        best_margin = -10**18
        best_res = res[0]
        for rx, ry in res:
            our_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            margin = opp_d - our_d
            if margin > best_margin or (margin == best_margin and our_d < md(nx, ny, best_res[0], best_res[1])):
                best_margin = margin
                best_res = (rx, ry)

        # Heuristics: favor progress toward center and slight avoidance of moving into tight obstacle areas.
        center_prog = -(md(nx, ny, cx, cy))
        # Obstacle proximity penalty (deterministic, small)
        prox = 0
        for ox2 in (-1, 0, 1):
            for oy2 in (-1, 0, 1):
                tx, ty = nx + ox2, ny + oy2
                if (tx, ty) in blocked:
                    prox += 1
        val = best_margin * 10 + center_prog * 0.5 - prox * 0.3

        if val > best_val or (val == best_val and [dx, dy] < best_move):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]