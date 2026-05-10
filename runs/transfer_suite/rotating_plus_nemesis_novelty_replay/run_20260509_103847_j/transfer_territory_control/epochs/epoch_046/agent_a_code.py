def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            obstacles.add((x, y))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    unT = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unT.append((x, y))
    unSet = set(unT)

    opT = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                opT.add((x, y))

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    frontier = []
    if selfT:
        for (x, y) in selfT:
            for dx, dy in neigh:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in unSet:
                    frontier.append((nx, ny))
    else:
        frontier = unT[:]

    if not frontier:
        frontier = unT[:]

    best = None
    best_score = None
    for (tx, ty) in frontier:
        # Prefer expansion from our territory, but also allow attacking near opponent.
        dist = abs(tx - sx) + abs(ty - sy)
        adj_self = 0
        if selfT:
            for dx, dy in neigh:
                if (tx + dx, ty + dy) in selfT:
                    adj_self = 1
                    break
        adj_op = 0
        if opT:
            for dx, dy in neigh:
                if (tx + dx, ty + dy) in opT:
                    adj_op = 1
                    break
        # Bias: closer, adjacent-to-self, adjacent-to-op (to deny/flip), and toward center slightly.
        center_bias = abs(tx - (w - 1) / 2.0) + abs(ty - (h - 1) / 2.0)
        score = dist - (5.0 if adj_self else 0.0) - (2.0 if adj_op else 0.0) + 0.01 * center_bias
        if best_score is None or score < best_score:
            best_score, best = score, (tx, ty)

    if best is None:
        return [0, 0]

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if not inb(nx, ny):
        # Try axis-only alternatives deterministically
        for ax, ay in [(dx, 0), (0, dy), (0, 0), (-dx, 0), (0, -dy)]:
            nnx, nny = sx + ax, sy + ay
            if inb(nnx, nny):
                return [int(ax), int(ay)]
        return [0, 0]
    return [int(dx), int(dy)]