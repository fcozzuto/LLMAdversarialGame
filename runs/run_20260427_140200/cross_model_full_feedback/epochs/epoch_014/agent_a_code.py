def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))
    resources = []
    for r in observation.get("resources", []) or []:
        if r is None or len(r) < 2:
            continue
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best, bestv = (0, 0), 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            v = dist((nx, ny), (tx, ty))
            if v < bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Pick a contested target where we are (or can become) earlier.
    best_t, best_score = resources[0], -10**18
    for tx, ty in resources:
        myd = dist((sx, sy), (tx, ty))
        opd = dist((ox, oy), (tx, ty))
        # Prefer targets we can reach no later, else the least-lose.
        lead = opd - myd
        # Add slight preference for closer-to-center to avoid deadlocks.
        center_bias = -0.01 * (abs(tx - (w - 1) / 2) + abs(ty - (h - 1) / 2))
        val = lead * 100 + center_bias - 0.1 * myd
        # Deterministic tie-break by coordinates
        if val > best_score or (val == best_score and (tx, ty) < best_t):
            best_score, best_t = val, (tx, ty)
    tx, ty = best_t

    # Move to improve our position relative to opponent at the chosen target.
    best_move, best_val = (0, 0), -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        myd = dist((nx, ny), (tx, ty))
        opd = dist((ox, oy), (tx, ty))
        # Higher is better: reduce our distance; increase opponent gap; avoid moving into obvious adjacency to obstacle-less walls not needed (lightweight).
        v = (opd - myd) * 100 - myd
        # If we're moving onto the resource, spike deterministically.
        if (nx, ny) == (tx, ty):
            v += 10**6
        # Small deterministic tie-break to prevent oscillation: prefer moves with lexicographically smallest (dx,dy)
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val, best_move = v, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]