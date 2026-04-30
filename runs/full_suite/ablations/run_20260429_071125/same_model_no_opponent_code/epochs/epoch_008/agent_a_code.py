def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {tuple(p) for p in observation.get("obstacles", [])}
    resources = [tuple(p) for p in observation.get("resources", [])]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def safe(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free_neighbors(nx, ny):
        c = 0
        for dx, dy in deltas:
            tx, ty = nx + dx, ny + dy
            if safe(tx, ty):
                c += 1
        return c

    # If surrounded, stay; otherwise evaluate moves.
    best = (0, 0)
    best_score = -10**18
    moved = False
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if safe(nx, ny):
            moved = True
            score = 0
            # Resource contest heuristic: prefer resources where we are closer than opponent.
            if resources:
                for rx, ry in resources:
                    d_me = cheb(nx, ny, rx, ry)
                    d_op = cheb(ox, oy, rx, ry)
                    closer_bonus = (d_op - d_me)
                    # Larger bonus when we can reach sooner; avoid giving opponent an advantage.
                    score += 30 * closer_bonus - 5 * d_me
                # Encourage being near at least one resource.
                dmin = min(cheb(nx, ny, rx, ry) for (rx, ry) in resources)
                score += 40 / (1 + dmin)
            # Obstacle avoidance / mobility
            score += 2 * free_neighbors(nx, ny)
            # Keep distance if opponent is close (avoid running into their routes)
            d_to_op = cheb(nx, ny, ox, oy)
            score -= 3 * (4 - d_to_op) if d_to_op < 4 else 0
            # Deterministic tie-break: prefer moves with smaller dx,dy lexicographic via score then order
            if score > best_score:
                best_score = score
                best = (dx, dy)

    if not moved:
        return [0, 0]
    return [best[0], best[1]]