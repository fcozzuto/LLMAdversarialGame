def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    # Choose a target resource favoring closer-than-opponent
    best = None
    best_val = None
    for r in resources:
        rx, ry = r
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Lower is better: ours distance weighted against opponent
        val = ds * 2 - do
        if best_val is None or val < best_val or (val == best_val and (rx < best[0] or (rx == best[0] and ry < best[1]))):
            best_val = val
            best = (rx, ry)
    tx, ty = best

    # Greedy move toward target with obstacle avoidance
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    pref = [(0, 0)] + [m for m in moves if m != (0, 0)]  # keep staying as last resort but deterministic
    bestm = None
    bestscore = None
    for dx, dy in pref:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nds = dist((nx, ny), (tx, ty))
        # Also lightly discourage moving into squares adjacent to obstacles
        adj = 0
        if (nx - 1, ny) in obstacles: adj += 1
        if (nx + 1, ny) in obstacles: adj += 1
        if (nx, ny - 1) in obstacles: adj += 1
        if (nx, ny + 1) in obstacles: adj += 1
        # Primary: reduce distance; Secondary: avoid obstacle-adjacent; Tertiary: deterministic order
        score = nds * 10 + adj
        if bestscore is None or score < bestscore or (score == bestscore and (dx, dy) < bestm):
            bestscore = score
            bestm = (dx, dy)

    if bestm is None:
        return [0, 0]
    return [bestm[0], bestm[1]]