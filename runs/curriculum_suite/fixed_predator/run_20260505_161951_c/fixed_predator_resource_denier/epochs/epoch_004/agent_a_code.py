def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def cheb(ax, ay, bx, by):
        da = abs(ax - bx)
        db = abs(ay - by)
        return da if da > db else db

    if not resources:
        best = (0, 0)
        best_key = (-10**9, -10**9)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obs:
                continue
            sep = cheb(nx, ny, ox, oy)
            key = (sep, -(abs(nx - w // 2) + abs(ny - h // 2)))
            if key > best_key or (key == best_key and (dx, dy) < best):
                best_key, best = key, (dx, dy)
        return [best[0], best[1]]

    best = (0, 0)
    best_key = (-10**18, 10**9, 10**9)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obs:
            continue
        max_val = -10**18
        best_sd = 10**9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            val = (od - sd) * 100 - sd
            if val > max_val:
                max_val = val
                best_sd = sd
            elif val == max_val and sd < best_sd:
                best_sd = sd
        opp_to_best = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
        key = (max_val + 2 * (opp_to_best - min(cheb(nx, ny, rx, ry) for rx, ry in resources)), best_sd, dx * 3 + dy)
        if key > best_key or (key == best_key and (dx, dy) < best):
            best_key, best = key, (dx, dy)
    return [best[0], best[1]]