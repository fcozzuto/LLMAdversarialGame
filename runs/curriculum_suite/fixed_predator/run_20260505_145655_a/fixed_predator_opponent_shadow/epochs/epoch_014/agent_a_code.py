def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h
    def sign(v): return 0 if v == 0 else (1 if v > 0 else -1)
    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        return [-sign(ox - x), -sign(oy - y)]
    best_dx, best_dy, best_sc = 0, 0, -10**18

    # Opportunistic: choose move that maximizes the best "win margin" over any resource,
    # while discouraging stepping into obstacles and avoiding moves that let opponent get closer.
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        md = dist(nx, ny, ox, oy)
        sc = 0
        local_best = -10**18
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # + if we are closer than opponent (good), - if not.
            margin = od - sd
            # Prefer resources we can reach sooner, and keep some pressure on opponent.
            val = margin * 100 - sd * 3 + md * (-1) + (0 if margin <= 0 else 10)
            if val > local_best:
                local_best = val
        sc = local_best
        # If we aren't creating a positive margin, fall back to best interception toward opponent.
        if sc < 0:
            sc = sc - dist(nx, ny, ox, oy) * 2
        # Tiny deterministic tie-breaker: prefer staying or moving toward top-left (lexicographic).
        sc += -0.001 * (nx * 8 + ny)
        if sc > best_sc:
            best_sc, best_dx, best_dy = sc, dx, dy
    return [int(best_dx), int(best_dy)]