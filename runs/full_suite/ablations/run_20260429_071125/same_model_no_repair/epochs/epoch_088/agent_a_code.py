def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            r = (int(p[0]), int(p[1]))
            if r not in obstacles:
                resources.append(r)

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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best = None
    best_val = None
    # Prefer stepping directly onto a resource when possible.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in resources:
            if best is None or (dx, dy) < best:
                best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    # Otherwise, minimize distance to the closest resource from the candidate cell.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_res = min(cheb(nx, ny, rx, ry) for (rx, ry) in resources)
        d_to_opp = cheb(nx, ny, ox, oy)
        # Tie-break deterministically: prefer larger distance from opponent, then lexicographic move.
        val = (d_to_res, -d_to_opp, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]