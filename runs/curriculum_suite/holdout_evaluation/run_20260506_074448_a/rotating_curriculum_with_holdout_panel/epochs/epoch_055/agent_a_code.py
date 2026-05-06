def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obs_list)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    turn = observation.get("turn_index", 0)

    if resources:
        if turn % 2 == 0:
            tx, ty = min(resources, key=lambda r: (man(ox, oy, r[0], r[1]), r[0], r[1]))
        else:
            tx, ty = min(resources, key=lambda r: (man(sx, sy, r[0], r[1]), r[0], r[1]))

        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                d = man(nx, ny, tx, ty)
                if best is None or d < best[0] or (d == best[0] and (dx, dy) < best[1]):
                    best = (d, (dx, dy))
        if best is not None:
            return [best[1][0], best[1][1]]

    # Fallback: move to maximize distance from opponent, avoiding obstacles.
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            d = man(nx, ny, ox, oy)
            if best is None or d > best[0] or (d == best[0] and (dx, dy) < best[1]):
                best = (d, (dx, dy))
    if best is not None:
        return [best[1][0], best[1][1]]

    return [0, 0]