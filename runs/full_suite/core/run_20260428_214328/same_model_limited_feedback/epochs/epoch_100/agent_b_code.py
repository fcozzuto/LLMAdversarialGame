def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_target():
        if not resources:
            return None
        best = None
        best_key = None
        for rx, ry in resources:
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # Prefer resources we can reach sooner; if not, prefer ones where opponent is much later.
            key = (ds, -(do - ds), (rx + 3 * ry))
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    target = best_target()
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # If target is not set or is blocked, run a defensive/spacing move: reduce chances of collision.
    if target is None:
        tx, ty = ox, oy
        def score_move(nx, ny):
            # Stay away from opponent while avoiding obstacles
            d = dist((nx, ny), (ox, oy))
            return (d, nx, ny)
    else:
        tx, ty = target
        def score_move(nx, ny):
            # Reduce distance to chosen target; if tied, keep away from opponent; avoid obstacles.
            d_t = dist((nx, ny), (tx, ty))
            d_o = dist((nx, ny), (ox, oy))
            return (-d_t, d_o, nx, ny)

    best_dx, best_dy = 0, 0
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        sc = score_move(nx, ny)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]