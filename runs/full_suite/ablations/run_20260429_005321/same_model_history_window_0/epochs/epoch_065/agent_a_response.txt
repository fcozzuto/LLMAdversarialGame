def choose_move(observation):
    x0, y0 = observation["self_position"]
    xo, yo = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_target(from_pos, prefer_opponent=False):
        if not resources:
            return (w // 2, h // 2)
        if prefer_opponent:
            # Prefer a resource closest to the opponent (to contest it).
            return min(resources, key=lambda r: (man(tuple(from_pos), r), man((xo, yo), r)))
        return min(resources, key=lambda r: (man(from_pos, r), man((xo, yo), r)))

    # Strategic change: contest the opponent's nearest resource more aggressively.
    self_target = best_target((x0, y0), prefer_opponent=False)
    opponent_target = best_target((xo, yo), prefer_opponent=True)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    if not resources:
        # No resources: move away from opponent while staying valid.
        for dx, dy in moves:
            nx, ny = x0 + dx, y0 + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            val = man((nx, ny), (xo, yo))
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    for dx, dy in moves:
        nx, ny = x0 + dx, y0 + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        newp = (nx, ny)

        ds = man(newp, self_target)
        do = man(newp, opponent_target)

        engage = 2.0 if man(newp, (xo, yo)) <= 1 else 0.0
        # Prefer: approach our target, but also contest opponent's target; engagement boosts.
        val = (-1.2 * ds) + (-0.9 * do) + engage

        # Mild tie-break: prefer moves that reduce distance to opponent while not improving ours too much (contesting).
        val += -0.1 * man(newp, (xo, yo))

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]