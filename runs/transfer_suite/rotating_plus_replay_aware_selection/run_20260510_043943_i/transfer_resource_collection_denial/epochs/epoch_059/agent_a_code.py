def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def man(ax, ay, bx, by):
        if ax < bx:
            ax, bx = bx, ax
        if ay < by:
            ay, by = by, ay
        return (ax - bx) + (ay - by)

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            nx, ny = sx, sy

        move_score = -10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            # Prefer resources we reach sooner than opponent.
            score = (od - sd) * 1000 - sd

            # If opponent likely to sweep their current row, deprioritize same-row targets.
            if ry == oy:
                score -= 120

            # Mild preference for nearer resources even when both are far.
            score -= (sd > 0) * 2

            if score > move_score:
                move_score = score

        # Tie-break deterministically toward progress: smaller distance to best target, then toward increasing x/y.
        if move_score > best_score:
            best_score = move_score
            best = (dx, dy)
        elif move_score == best_score:
            if (abs(dx) + abs(dy), -dx, -dy) < (abs(best[0]) + abs(best[1]), -best[0], -best[1]):
                best = (dx, dy)

    return [int(best[0]), int(best[1])]