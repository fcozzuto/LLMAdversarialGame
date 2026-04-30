def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    obst = {(p[0], p[1]) for p in obstacles}

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Target selection: prioritize resources that we can reach sooner than opponent, with tie-break by closeness.
    tx, ty = x, y
    if resources:
        best = None
        for rx, ry in resources:
            ds = d2(rx, ry, x, y)
            do = d2(rx, ry, ox, oy)
            # Win-favoring objective: large (opponent farther than us).
            val = (do - ds)
            # Small tie-break toward nearer absolute distance.
            val = val * 10 - ds
            if best is None or val > best[0]:
                best = (val, rx, ry)
        tx, ty = best[1], best[2]
    else:
        # If no visible resources, push to a corner opposite opponent to deny.
        tx = 0 if ox > x else w - 1
        ty = 0 if oy > y else h - 1

    best_move = (0, 0)
    best_val = -10**18

    # Try to avoid moving into trap: keep distance from opponent while still approaching target.
    # Also slightly discourage staying still unless it is best.
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        # Core: approach target.
        approach = -d2(nx, ny, tx, ty)

        # Opponent interaction: prefer moves that keep opponent farther, and also avoid giving them direct access.
        opp_far = d2(nx, ny, ox, oy)
        block = -abs((nx - ox) + (ny - oy))  # simple deterministic bias against moving toward opponent.

        # Resource pickup preference: moving onto resource is highly rewarded.
        on_res = 0
        for rx, ry in resources:
            if nx == rx and ny == ry:
                on_res = 1
                break

        # Mild "progress" bias: discourage stagnation.
        stay_pen = -0.15 if (dx == 0 and dy == 0) else 0.0

        val = approach * 1.6 + opp_far * 0.07 + block * 0.02 + on_res * 1000 + stay_pen

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]