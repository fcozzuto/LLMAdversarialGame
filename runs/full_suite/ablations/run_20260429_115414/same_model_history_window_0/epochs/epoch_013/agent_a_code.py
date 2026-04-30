def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def clamp_move(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    best = (-(10**9), 0, 0)

    if not resources:
        # No resources: try to stay safe by not walking into obstacles (prefer toward opponent slightly)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not clamp_move(nx, ny):
                continue
            d_op = manhattan((nx, ny), (ox, oy))
            val = -d_op
            if val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_move(nx, ny):
            continue

        best_val = -(10**9)
        for rx, ry in resources:
            sd = manhattan((nx, ny), (rx, ry))
            od = manhattan((ox, oy), (rx, ry))
            # Prefer resources we're closer to; otherwise fall back to closest
            score = (od - sd) * 4 - sd
            if score > best_val:
                best_val = score

        # Small tie-break: keep moving generally toward the most favorable resource region
        val = best_val - 0.01 * manhattan((nx, ny), (ox, oy))
        if val > best[0]:
            best = (val, dx, dy)

    if best[0] == -(10**9):
        return [0, 0]
    return [best[1], best[2]]