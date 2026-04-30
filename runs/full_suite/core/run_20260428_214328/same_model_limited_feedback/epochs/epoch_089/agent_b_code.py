def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    width, height = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(px, py):
        return 0 <= px < width and 0 <= py < height

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # If no resources, drift away from opponent and avoid obstacles.
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            score = (-manh(nx, ny, ox, oy), nx, ny)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        if best:
            return [best[1], best[2]]
        return [0, 0]

    # Choose a target: close to us, comparatively far from opponent.
    target = None
    best_t = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = manh(x, y, rx, ry)
        do = manh(ox, oy, rx, ry)
        val = ds - 0.6 * do
        key = (val, ds, -do, rx, ry)
        if best_t is None or key < best_t:
            best_t = key
            target = (rx, ry)

    rx, ry = target
    best = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        dnew = manh(nx, ny, rx, ry)
        dopp = manh(nx, ny, ox, oy)
        # Prefer smaller distance to target, and larger distance from opponent.
        score = (dnew, -dopp, nx, ny)
        if best is None or score < best[0]:
            best = (score, dx, dy)

    if best:
        return [best[1], best[2]]
    return [0, 0]