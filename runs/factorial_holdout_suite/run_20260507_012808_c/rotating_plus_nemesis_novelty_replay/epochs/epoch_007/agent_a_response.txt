def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is not None and len(r) >= 2:
            rt = (int(r[0]), int(r[1]))
            if rt not in obstacles:
                resources.append(rt)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    def mdist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Race heuristic: prioritize resources where we are closer than opponent.
    best_move = (0, 0)
    best_score = None
    for dx, dy, nx, ny in cand:
        cur = None
        for rx, ry in resources:
            d_me = mdist((nx, ny), (rx, ry))
            d_op = mdist((ox, oy), (rx, ry))
            # Higher is better; add immediate-collection bias.
            val = (d_op - d_me)
            if d_me == 0:
                val += 1000
            else:
                val += 20 / (1 + d_me)
            # Penalize moves that drift away from any resource.
            val -= 0.1 * (abs(nx - sx) + abs(ny - sy))
            if cur is None or val > cur:
                cur = val
        # If no resources, go toward opponent-facing diagonal (still deterministic).
        if cur is None:
            cur = -mdist((nx, ny), (ox, oy))
        if best_score is None or cur > best_score:
            best_score = cur
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]