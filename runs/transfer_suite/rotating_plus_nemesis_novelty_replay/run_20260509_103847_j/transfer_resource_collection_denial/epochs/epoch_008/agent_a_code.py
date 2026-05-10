def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a resource to contest: prefer ones we can arrive no later than opponent, else the least losing race.
    opp = (ox, oy)
    best_r = None
    best_key = None
    for r in resources:
        sd = md((sx, sy), r)
        od = md(opp, r)
        slack = od - sd  # higher means we are closer
        key = (sd > od, -slack, sd, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best_r = r

    tx, ty = best_r

    # Pick the move that improves our race against the chosen target, while avoiding obstacles/out of bounds.
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd2 = abs(nx - tx) + abs(ny - ty)
        od2 = abs(ox - tx) + abs(oy - ty)
        slack2 = od2 - sd2
        # Prefer valid moves with better slack; slight preference for getting closer; deterministic tie-break.
        cand.append(((sd2 > od2, -slack2, sd2, nx, ny), (dx, dy)))

    if cand:
        cand.sort(key=lambda t: t[0])
        return [cand[0][1][0], cand[0][1][1]]

    return [0, 0]