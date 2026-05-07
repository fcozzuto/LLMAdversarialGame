def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    if not resources:
        return [0, 0]

    obs = set(map(tuple, obstacles))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        # Use Chebyshev distance to reflect diagonal move capability deterministically
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def step_options():
        return [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Target: maximize advantage where we're significantly closer than the opponent.
    best_t = None
    best_v = None
    for r in resources:
        myd = dist((sx, sy), r)
        opd = dist((ox, oy), r)
        # Favor: we are closer; also prefer shorter myd as tiebreak.
        v1 = opd - myd
        v2 = -myd
        # Mild bias away from opponent by preferring resources far from them when advantage ties
        v3 = myd - opd
        key = (v1, v2, v3, -r[0], -r[1], r[0], r[1])
        if best_v is None or key > best_v:
            best_v = key
            best_t = r

    tx, ty = best_t
    candidates = []
    for dx, dy in step_options():
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nd_my = dist((nx, ny), (tx, ty))
        nd_op = dist((nx, ny), (ox, oy))
        # Prefer reducing distance to target, and slightly prefer moving away from opponent.
        val = (-(nd_my), nd_op, nx, ny)
        candidates.append((val, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(reverse=True)
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]