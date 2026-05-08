def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    dmax = lambda x, y: max(abs(x - ox), abs(y - oy))  # Chebyshev distance

    role = str(observation.get("self_role", "pursuer") or "pursuer").lower()
    evade = ("evad" in role) or ("run" in role) or ("away" in role)

    best = None
    bestv = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = dmax(nx, ny)
        v = dist if evade else -dist
        if best is None or v > bestv:
            best, bestv = (dx, dy), v

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]