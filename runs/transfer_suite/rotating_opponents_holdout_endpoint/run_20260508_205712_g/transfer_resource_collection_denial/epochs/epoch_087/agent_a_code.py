def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    resources.sort()

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Prefer moves that secure a resource earlier than the opponent.
        cur_best = -10**18
        for rx, ry in resources:
            sd = abs(rx - nx) if abs(rx - nx) > abs(ry - ny) else (abs(ry - ny))
            od = abs(rx - ox) if abs(rx - ox) > abs(ry - oy) else (abs(ry - oy))
            # Chebyshev distance for diagonal movement.
            # Higher is better: lead over opponent, then closeness.
            val = (od - sd) * 1000 - sd
            # Small deterministic tie-break to avoid jitter.
            if (rx + 31 * ry) % 7 == 0:
                val -= 0.1
            if val > cur_best:
                cur_best = val

        # Add slight preference for staying mobile: count accessible neighbors.
        neigh = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty):
                neigh += 1
        cur_total = cur_best + neigh * 0.01

        if cur_total > best_val:
            best_val = cur_total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]