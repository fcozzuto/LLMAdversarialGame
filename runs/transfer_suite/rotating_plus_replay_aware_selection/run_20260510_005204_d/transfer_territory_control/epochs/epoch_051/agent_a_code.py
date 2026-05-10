def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dcur = abs(sx - ox) + abs(sy - oy)
        dnew = abs(nx - ox) + abs(ny - oy)
        if dnew == 0:
            return [dx, dy]
        # Prefer reducing distance; slight tie-break toward board center for stability.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = -(abs(nx - cx) + abs(ny - cy)) * 0.001
        val = (dcur - dnew) * 1000 + center_bias - (abs(dx) + abs(dy)) * 0.01
        if val > best_val or (val == best_val and (best is None or (dx, dy) < best)):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]