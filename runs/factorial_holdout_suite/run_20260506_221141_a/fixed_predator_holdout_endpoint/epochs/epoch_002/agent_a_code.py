def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obs = set((a, b) for a, b in obstacles)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def md(px, py, qx, qy):
        return abs(px - qx) + abs(py - qy)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = (None, -10**9, 0, 0)  # (target, val, nx, ny)
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        selfd = md(x, y, rx, ry)
        oppd = md(ox, oy, rx, ry)
        # If opponent is closer, prefer resources that force a divergence (denial), else go for them.
        val = (10 - oppd) - (8 - selfd) + (1 if selfd <= oppd else -2) + (0.01 * (rx + ry))
        if best[0] is None or val > best[1]:
            best = (rx, val, rx, ry)

    tx, ty = best[0], best[3]
    if tx is None:
        return [0, 0]

    # Obstacle-aware greedy step: maximize (opponent-relative progress to target) plus avoid moving near opponent when behind.
    target_dx = 0 if tx == x else (1 if tx > x else -1)
    target_dy = 0 if ty == y else (1 if ty > y else -1)
    behind = md(x, y, ox, oy) > md(ox, oy, x, y)

    bestm = (0, 0, 0)  # val, dx, dy
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        self_now = md(x, y, tx, ty)
        self_next = md(nx, ny, tx, ty)
        opp_now = md(ox, oy, tx, ty)
        # approximate opponent move influence: if we step toward where opponent also can reach faster, penalize.
        opp_next = opp_now
        progress = self_now - self_next
        rel = (opp_now - self_next) - (opp_next - opp_next)
        dist_opp = md(nx, ny, ox, oy)
        penalty = 0
        if behind and dist_opp <= 2:
            penalty -= 1.5
        # Prefer using the component that moves toward target; mild tie-break to avoid oscillation.
        align = (1 if dx == target_dx else 0) + (1 if dy == target_dy else 0)
        val = 3.0 * progress + 1.2 * rel + 0.15 * align + penalty
        if bestm[0] is None or val > bestm[0]:
            bestm = (val, dx, dy)

    dx, dy = bestm[1], bestm[2]
    # If all candidate moves blocked, stay.
    if not inb(x + dx, y + dy):
        return [0, 0]
    return [dx, dy]