def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]
    if resources:
        obs_set = set((x, y) for x, y in obstacles)
        def dist2(a, b):
            dx = a[0] - b[0]
            dy = a[1] - b[1]
            return dx * dx + dy * dy
        best_r = None
        best_key = None
        for r in resources:
            d_self = dist2((sx, sy), r)
            d_opp = dist2((ox, oy), r)
            key = d_self - 0.35 * d_opp  # favor resources we are relatively closer to
            if best_key is None or key < best_key or (key == best_key and r < best_r):
                best_key = key
                best_r = r
        tx, ty = best_r
    else:
        obs_set = set((x, y) for x, y in obstacles)
        tx, ty = (w // 2), (h // 2)

    moves = [[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
    def clamp(v, lo, hi):
        if v < lo: return lo
        if v > hi: return hi
        return v

    def score_move(nx, ny):
        if (nx, ny) in obs_set:
            return -10**12
        dt = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        do = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # If resources exist, add a tiny bias to stepping onto a resource
        res_bias = 0
        if resources:
            if (nx, ny) in set((x, y) for x, y in resources):
                res_bias = 5000
        # Prefer reducing distance to target and increasing distance from opponent
        return (-dt) + 0.18 * do + res_bias

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx = clamp(sx + dx, 0, w - 1)
        ny = clamp(sy + dy, 0, h - 1)
        val = score_move(nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]