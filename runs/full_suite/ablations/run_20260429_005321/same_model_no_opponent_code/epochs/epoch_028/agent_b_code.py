def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            rx, ry = r[0], r[1]
            if (rx, ry) not in obs:
                resources.append((rx, ry))

    def md(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if inside(x + dx, y + dy)]
    if not moves:
        return [0, 0]

    if resources:
        best_res = None
        best_key = None
        for rx, ry in resources:
            sd = md(x, y, rx, ry)
            od = md(ox, oy, rx, ry)
            # Prefer resources we can reach soon, while discouraging ones opponent is much closer to.
            key = (sd - int(0.8 * od), rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_res = (rx, ry)
        tx, ty = best_res
        if (x, y) == (tx, ty):
            return [0, 0]

        best_move = None
        best_key = None
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            k = (md(nx, ny, tx, ty), md(nx, ny, ox, oy), tx, ty, dx, dy)
            if best_key is None or k < best_key:
                best_key = k
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: move toward the opponent to secure control.
    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        k = (md(nx, ny, ox, oy), nx, ny, dx, dy)
        if best_key is None or k < best_key:
            best_key = k
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]