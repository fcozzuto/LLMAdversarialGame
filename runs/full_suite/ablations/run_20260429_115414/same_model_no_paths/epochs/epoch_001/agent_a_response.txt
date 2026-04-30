def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy  # Chebyshev

    def score_target(t):
        d1 = dist((sx, sy), t)
        d2 = dist((ox, oy), t)
        return (d2 - d1, -d1)  # prefer resources opponent is worse at + closer

    if not resources:
        tx, ty = (w//2, h//2)
    else:
        # Deterministically pick best target; tie-break by coordinates
        best = None
        for r in resources:
            key = score_target(r) + (-r[0], -r[1])
            if best is None or key > best[0]:
                best = (key, r)
        tx, ty = best[1]

    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = dist((nx, ny), (tx, ty))
        # If opponent is closer to that resource, try to reduce our distance more
        od = dist((ox, oy), (tx, ty))
        candidates.append((nd, od - nd, nx, ny, dx, dy))
    # Choose move that minimizes our distance; then maximizes advantage; deterministic tie-break
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda z: (z[0], -z[1], z[2], z[3]))
    return [candidates[0][4], candidates[0][5]]