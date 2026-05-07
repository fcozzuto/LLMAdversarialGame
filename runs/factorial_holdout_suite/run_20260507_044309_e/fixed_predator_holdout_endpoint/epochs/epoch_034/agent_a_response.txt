def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_val = -10**18

    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        move_val = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            cur_myd = cheb(sx, sy, rx, ry)

            # Resource denial: if we can be (or become) at least as close as opponent, strongly favor.
            if myd <= oppd:
                val = 10 - myd + (oppd - myd)
            else:
                # If opponent is closer, discourage, but still prefer resources where we improve a lot.
                val = -2 - myd + (cur_myd - myd)

            # Light preference to nearer resources overall (tie-break style).
            val += 0.2 * (opd := (cheb(ox, oy, rx, ry)))  # deterministic extra term
            move_val = val if val > move_val else move_val

        # Mild anti-stall: if equally good, prefer moving.
        if move_val > best_val or (move_val == best_val and (dxm != 0 or dym != 0) and best == [0, 0]):
            best_val = move_val
            best = [dxm, dym]

    return best