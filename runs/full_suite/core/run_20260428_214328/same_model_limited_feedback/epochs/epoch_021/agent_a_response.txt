def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = {tuple(p) for p in observation.get("obstacles", [])}
    resources = [tuple(p) for p in observation.get("resources", [])]
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    def clamp_step(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h: return (x, y)
        if (nx, ny) in obstacles: return (x, y)
        return (nx, ny)

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Pick a target resource we are more likely to reach than the opponent.
    best_r = None; best_bias = -10**9
    for r in resources:
        sd = dist((sx, sy), r); od = dist((ox, oy), r)
        bias = (od - sd)  # positive means we are closer
        # Encourage taking resources that are not already too far away for us.
        bias += -0.05 * sd
        if bias > best_bias:
            best_bias = bias; best_r = r

    # If we're not advantaged for any resource, switch to closest-to-we-want while keeping distance from opponent.
    if best_bias <= 0:
        best_r = min(resources, key=lambda r: dist((sx, sy), r))

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_m = (0, 0); best_score = -10**18
    for dx, dy in deltas:
        nx, ny = clamp_step(sx, sy, dx, dy)
        # Attract to target; avoid getting closer to opponent too much.
        d_t = dist((nx, ny), best_r)
        d_o = dist((nx, ny), (ox, oy))
        # If stepping onto a resource tile, prioritize heavily.
        on_res = 1 if (nx, ny) in obstacles else 0
        on_target = 1 if (nx, ny) == best_r else 0
        # Also slightly prefer moves that reduce distance to target (greedy).
        score = (-10*d_t) + (2.5*d_o) + (50*on_target) - (2*on_res)
        # Small deterministic tie-break: prefer fewer changes earlier in list order by adding index penalty.
        idx_pen = 0
        if dx == 0 and dy == 0: idx_pen = 0.01
        score -= idx_pen
        if score > best_score:
            best_score = score; best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]