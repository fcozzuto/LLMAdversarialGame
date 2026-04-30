def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}
    resources = observation.get("resources") or []

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dcheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_val = -10**18

    # If no resources listed, just move toward center while avoiding obstacles.
    if not resources:
        tx, ty = int(round(cx)), int(round(cy))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            val = -dcheb(nx, ny, tx, ty)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Choose the move that maximizes our advantage over the opponent for the best reachable resource.
        move_val = -10**18
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            ds = dcheb(nx, ny, rx, ry)
            do = dcheb(ox, oy, rx, ry)
            # Strongly prefer resources where we arrive earlier; tie-break for sooner arrival and closeness.
            val = (do - ds) * 1000 - ds * 3 - (abs(rx - cx) + abs(ry - cy)) * 0.1
            if ds == do:
                val += 5
            if val > move_val:
                move_val = val
        # Small preference for staying aligned with the best resource direction (encourages forward motion).
        move_val += -dcheb(nx, ny, cx, cy) * 0.01
        if move_val > best_val:
            best_val = move_val
            best_move = (dx, dy)

    # If all moves blocked (rare), stay.
    return [int(best_move[0]), int(best_move[1])]