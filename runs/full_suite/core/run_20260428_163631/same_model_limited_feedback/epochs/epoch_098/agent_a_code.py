def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        for rx, ry in resources:
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; tie-break by ds then coordinates.
            key = (-(do - ds), ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_step = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        ds = cheb(nx, ny, tx, ty)
        # Small tie-break: avoid moving toward opponent when distances are similar.
        da = cheb(nx, ny, ox, oy)
        score = (ds, da, abs((nx - tx)) + abs((ny - ty)), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]