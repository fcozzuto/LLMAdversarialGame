def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)  # Chebyshev

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        bestv = 10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                v = dist((nx, ny), (tx, ty)) + 0.01 * (abs(nx - (w - 1)) + abs(ny - (h - 1)))
                if v < bestv:
                    bestv = v
                    best = [dx, dy]
        return best

    # Resource denial heuristic: maximize advantage in getting to resources sooner than opponent,
    # while also increasing opponent's nearest-resource distance.
    res_set = set(tuple(r) for r in resources)
    best = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        self_near = min(dist((nx, ny), r) for r in resources)
        opp_near = min(dist((ox, oy), r) for r in resources)

        # If we can step onto a resource, strongly prefer it.
        take_bonus = -5 if (nx, ny) in res_set else 0

        # Deny opponent by preferring moves that improve our lead AND worsen their effective access.
        # Since opponent position is fixed within the turn, use "would-be lead" and "resource closeness delta".
        lead = opp_near - self_near  # higher is better (we closer than opp)
        key = (-(lead + take_bonus), self_near, -lead, nx + ny, nx, ny, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]
    return best