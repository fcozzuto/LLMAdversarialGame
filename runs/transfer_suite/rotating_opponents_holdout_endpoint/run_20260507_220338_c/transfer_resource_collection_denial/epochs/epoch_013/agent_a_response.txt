def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Race score: prefer moves that let us beat the opponent to some resource.
        move_best = -10**18
        for i, (rx, ry) in enumerate(resources):
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)

            # If we step onto a resource, huge.
            if nx == rx and ny == ry:
                s = 10**9 - i
            else:
                # Advantage: opponent distance minus our distance; also prefer closeness (small sd)
                s = (od - sd) * 1000 - sd * 3 - i
            if s > move_best:
                move_best = s

        # Mild tie-breaker: prefer staying/moving that reduces our distance to the nearest resource overall.
        if move_best > best[0]:
            best = (move_best, dx, dy)

    return [best[1], best[2]]