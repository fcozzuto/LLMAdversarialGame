def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def best_resource_for_step(nx, ny):
        if not resources:
            return -(man(nx, ny, ox, oy))
        best = -10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # prioritize winning the race to the resource, then proximity
            val = (do - ds) * 1000 - ds - do // 2
            # if we're effectively adjacent, strongly commit
            if ds == 0:
                val += 10**9
            elif ds == 1:
                val += 10**5
            if val > best:
                best = val
        return best

    best_move = [0, 0]
    best_score = -10**18

    # If no resources, drift toward opponent to contest space deterministically.
    if not resources:
        tx = 0 if ox == sx else (1 if ox > sx else -1)
        ty = 0 if oy == sy else (1 if oy > sy else -1)
        return [tx, ty]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        sc = best_resource_for_step(nx, ny)
        # tie-break toward larger progress on Manhattan toward the chosen resource
        if sc > best_score:
            best_score = sc
            best_move = [dx, dy]

    return best_move