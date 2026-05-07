def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b):
        # Chebyshev distance matches diagonal movement
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Choose a resource we are likely to reach first, else intercept by minimizing opponent advantage.
    best = None
    best_key = None
    for rx, ry in resources:
        d_me = dist((sx, sy), (rx, ry))
        d_op = dist((ox, oy), (rx, ry))
        # Key: prioritize resources where we are closer; then closer overall; then tie-break by coordinates.
        key = (d_op - d_me, -d_me, -rx, -ry)
        if best is None or key > best_key:
            best, best_key = (rx, ry), key

    tx, ty = best

    moves = [(0, 0), (1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
    # Greedy step that reduces distance to target; if tied, avoids opponent (interceptor flavor).
    bestm = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to = dist((nx, ny), (tx, ty))
        d_opp = dist((nx, ny), (ox, oy))
        # minimize d_to; maximize d_opp to keep separation when similar progress
        val = (d_to, -d_opp, abs(nx - tx) + abs(ny - ty), -dx, -dy)
        if bestv is None or val < bestv:
            bestv = val
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]