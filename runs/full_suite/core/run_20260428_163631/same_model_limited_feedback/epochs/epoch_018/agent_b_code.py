def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick a resource that we are relatively closest to (strong contesting behavior).
    if resources:
        best = None
        for r in resources:
            rx, ry = r
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            rel = ds - do
            key = (rel, ds, cheb(ox, oy, rx, ry), rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        target = best[1] if best is not None else None
    else:
        target = None

    if target is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = target

    # Move toward target while avoiding obstacles; if tied, move to reduce opponent access.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)

        # primary: get closer to target, secondary: keep distance from opponent (deny/avoid),
        # tertiary: prefer moving (reduce staying) deterministically.
        score = (d_to_t, -d_to_o, abs(dx) + abs(dy), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move