def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set(tuple(p) for p in obstacles)

    def man(a, b, c, d):
        x = a - c
        if x < 0:
            x = -x
        y = b - d
        if y < 0:
            y = -y
        return x + y

    best = [0, 0]
    best_val = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
                continue

            oppd = man(nx, ny, ox, oy)
            if resources:
                mind = 10**9
                for rx, ry in resources:
                    d = man(nx, ny, rx, ry)
                    if d < mind:
                        mind = d
                val = (-mind) + 0.25 * oppd
            else:
                cx, cy = w // 2, h // 2
                val = man(nx, ny, ox, oy) + (-man(nx, ny, cx, cy))

            if val > best_val:
                best_val = val
                best = [dx, dy]
    return best