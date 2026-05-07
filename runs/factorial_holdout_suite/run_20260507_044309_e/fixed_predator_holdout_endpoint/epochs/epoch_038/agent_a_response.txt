def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
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

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate move by best resource opportunity for us while considering opp distance.
        best_here = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)

            # Big reward if we can be no worse than opponent.
            lead = oppd - myd
            val = lead * 200 - myd
            if myd <= oppd:
                val += 10000

            # Small penalty if we are extremely far while opponent is close.
            if oppd <= 1 and myd > oppd:
                val -= 2000

            if val > best_here:
                best_here = val

        # Tie-break deterministically toward staying closer to current best resource.
        if best_here > best_val:
            best_val = best_here
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]