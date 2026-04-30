def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick best target resource based on our closeness and opponent remoteness.
    if resources:
        best = None
        best_val = 10**9
        for rx, ry in resources:
            our_d = cheb(sx, sy, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Prefer targets we can reach earlier; also prefer those far from opponent.
            val = our_d * 10 - opp_d * 3
            if val < best_val:
                best_val = val
                best = (rx, ry)
        tx, ty = best
    else:
        # If no resources, go for safer positioning: maximize distance from opponent and nudge toward our corner.
        tx, ty = 0 if sx <= w // 2 else w - 1, 0 if sy <= h // 2 else h - 1

    def obst_adj_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    pen += 2 if dx != 0 and dy != 0 else 1
        return pen

    # Score candidate moves.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        our_to = cheb(nx, ny, tx, ty)
        opp_to = cheb(ox, oy, tx, ty)
        # Higher is better: reduce our distance, increase opponent distance; penalize proximity to obstacles.
        score = -our_to * 10 + opp_to * 3 - obst_adj_pen(nx, ny)

        # Extra: if resource is exactly reached, heavily prefer it.
        if resources and (nx, ny) in set(resources):
            score += 10**6

        # Tie-break deterministically by preferring moves in a fixed order.
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]