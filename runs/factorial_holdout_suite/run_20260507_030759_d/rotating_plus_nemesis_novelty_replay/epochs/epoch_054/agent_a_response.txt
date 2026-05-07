def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
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
            cell = (int(r[0]), int(r[1]))
            if cell not in obstacles:
                resources.append(cell)

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
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # If stepping onto a resource, prioritize strongly.
        step_val = 0
        for (rx, ry) in resources:
            if rx == nx and ry == ny:
                step_val += 1000
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach earlier; penalize those they can.
            # Also add slight tie-break toward closer overall.
            margin = d_op - d_me
            step_val += (margin * 60) - (d_me * 3)

        # Small nudge: if we're currently adjacent/at a resource, don't wander.
        cur_adj = min(cheb(sx, sy, rx, ry) for (rx, ry) in resources)
        nxt_adj = min(cheb(nx, ny, rx, ry) for (rx, ry) in resources)
        step_val += (cur_adj - nxt_adj) * 10

        if step_val > best_val or (step_val == best_val and (dx, dy) < best_move):
            best_val = step_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]