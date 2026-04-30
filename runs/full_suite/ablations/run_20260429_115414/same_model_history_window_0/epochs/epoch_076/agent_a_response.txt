def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def step_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        # try axis-aligned fallbacks deterministically
        for ddx, ddy in [(dx, 0), (0, dy), (0, 0), (-dx, 0), (0, -dy)]:
            nx, ny = sx + ddx, sy + ddy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [ddx, ddy]
        return [0, 0]

    if resources:
        def dist(a, b):
            # Chebyshev distance works well with diagonal moves
            return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # Prefer resources where we are strictly closer; then minimize our distance;
            # break ties by preferring farther from opponent and lower coordinates (deterministic).
            key = (0 if ds < do else 1, ds, -do, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)

        tx, ty = best
        return step_toward(tx, ty)

    # No resources: drift toward center while avoiding obstacles
    cx, cy = (w - 1) // 2, (h - 1) // 2
    dx = 0 if cx == sx else (1 if cx > sx else -1)
    dy = 0 if cy == sy else (1 if cy > sy else -1)
    for ddx, ddy in [(dx, dy), (dx, 0), (0, dy), (0, 0)]:
        nx, ny = sx + ddx, sy + ddy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [ddx, ddy]
    return [0, 0]