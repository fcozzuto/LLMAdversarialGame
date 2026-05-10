def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in self_role) or ("catch" in self_role) or ("hunter" in self_role)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def free(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 1), (-1, -1), (1, -1), (-1, 1), (1, 0), (-1, 0), (0, 1), (0, -1)]

    def legal(pos):
        px, py = pos
        out = []
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if free(nx, ny):
                out.append((nx, ny))
        return out

    # If we're adjacent enough to step onto them, do it immediately.
    if pursuer:
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if (nx, ny) == (ox, oy):
                return [int(dx), int(dy)]
    else:
        # If we're evader, step away to maximize immediate distance if possible.
        best = (cheb(x, y, ox, oy), (0, 0))
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not free(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            if d > best[0] or (d == best[0] and (dx, dy) < best[1]):
                best = (d, (dx, dy))
        return [int(best[1][0]), int(best[1][1])]

    my_legal = legal((x, y))
    op_legal = legal((ox, oy))
    best_move = (0, 0)
    best_val = None  # lower is better for pursuer (minimax worst-case distance)

    for nx, ny in my_legal:
        if (nx, ny) == (ox, oy):
            return [nx - x, ny - y]
        # opponent moves adversarially: maximize distance to our resulting position
        worst = -1
        for nox, noy in op_legal:
            d = cheb(nox, noy, nx, ny)
            if d > worst:
                worst = d
        val = worst
        if best_val is None or val < best_val or (val == best_val and (nx - x, ny - y) < best_move):
            best_val = val
            best_move = (nx - x, ny - y)

    return [int(best_move[0]), int(best_move[1])]