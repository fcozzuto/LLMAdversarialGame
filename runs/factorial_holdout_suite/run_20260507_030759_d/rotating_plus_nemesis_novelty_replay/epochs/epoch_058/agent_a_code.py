def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-break order: already fixed by moves list.

    best = (0, 0)
    best_val = -10**18
    # Opponent archetype sweeps rows: bias toward resources that are "safer" (opponent farther)
    # and that we can reach quickly.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = 0
        # If we can pick a resource immediately, prioritize heavily.
        for (rx, ry) in resources:
            if nx == rx and ny == ry:
                val += 100000
            else:
                d_me = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                # Maximize the lead we have over opponent at that target.
                # Weight opponent distance more to prevent easy steals.
                val += (d_op - d_me) * 50 - d_me * 5
        # Small preference for staying closer to the frontier between corners (diagonal pressure)
        val -= cheb(nx, ny, 7, 7) * 0.5
        if val > best_val:
            best_val = val
            best = (dx, dy)

    # If for some reason no valid move found (shouldn't happen), stop.
    return [int(best[0]), int(best[1])]