def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def md(a, b, c, d):
        ax = a - c
        if ax < 0: ax = -ax
        by = b - d
        if by < 0: by = -by
        return ax + by

    # If opponent is already very close, prioritize contesting a resource, otherwise go for best capture.
    contested_bias = 1.2 if md(sx, sy, ox, oy) <= 3 else 1.0

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if resources:
            val = 0.0
            for rx, ry in resources:
                d_me = md(nx, ny, rx, ry)
                d_op = md(ox, oy, rx, ry)
                # Capture priority: prefer resources we reach no later than opponent.
                if d_me <= d_op:
                    val += contested_bias * (30.0 - 2.2 * d_me - 1.0 * (d_op - d_me))
                else:
                    # Still allow progress, but discount strongly.
                    gap = d_me - d_op
                    val -= 6.0 + 2.8 * d_me + 3.0 * gap
                # Tie-break: move slightly toward center while still being capture-oriented.
                val -= 0.01 * (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
                # Mild repulsion from opponent to avoid suicidal approaches to contested cells.
                val -= 0.02 * md(nx, ny, ox, oy)
            # Prefer staying put if it captures immediately.
            if any((nx == rx and ny == ry) for rx, ry in resources):
                val += 50.0
        else:
            # No visible resources: move to increase distance from edges and reduce collision risk.
            val = -(0.5 * (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)) +
                    0.08 * md(nx, ny, ox, oy))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]