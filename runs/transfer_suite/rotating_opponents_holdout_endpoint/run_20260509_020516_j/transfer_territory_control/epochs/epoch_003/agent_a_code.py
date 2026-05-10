def choose_move(observation):
    W = int(observation.get("grid_width", 0) or 0)
    H = int(observation.get("grid_height", 0) or 0)
    if W <= 0 or H <= 0:
        return [0, 0]

    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [sp[0], sp[1]]) or [sp[0], sp[1]]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for c in obstacles:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            obs.add((int(c[0]), int(c[1])))

    unclaimed = observation.get("unclaimed_cells", []) or []
    targets = []
    for c in unclaimed:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if (x, y) not in obs:
                targets.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (W - 1) * 0.5, (H - 1) * 0.5

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    if not targets:
        candidates = [(x, y) for dx, dy in dirs for x, y in [(sx + dx, sy + dy)] if inb(x, y) and (x, y) not in obs]
        if not candidates:
            return [0, 0]
        tx, ty = min(candidates, key=lambda p: abs(p[0] - cx) + abs(p[1] - cy))
        return [tx - sx, ty - sy]

    turn = int(observation.get("turn_index", 0) or 0)
    prefer_center = (turn % 3 != 0)
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Score: reward approaching unclaimed, and optionally contesting opponent.
        val = 0
        for tx, ty in targets:
            d = abs(tx - nx) + abs(ty - ny)
            if d == 0:
                val += 10**7
            else:
                val += 1000.0 / d
        val *= 1.0
        if prefer_center:
            val += -0.3 * (abs(nx - cx) + abs(ny - cy))
        else:
            val += 0.6 * (-abs(nx - ox) - abs(ny - oy))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]