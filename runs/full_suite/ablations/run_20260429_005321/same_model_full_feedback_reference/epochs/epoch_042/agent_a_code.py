def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_target():
        if not resources:
            return (w // 2, h // 2)
        best = resources[0]
        bestv = -10**18
        for (x, y) in resources:
            ds = cheb(sx, sy, x, y)
            do = cheb(ox, oy, x, y)
            # Prefer targets where we are closer than opponent; penalize if opponent is already on/adjacent.
            v = (do - ds) * 100 - ds
            if do <= 1: v -= 200
            # Prefer slightly central-ish targets when tied.
            v -= (abs(x - (w - 1) / 2) + abs(y - (h - 1) / 2)) * 0.1
            if v > bestv:
                bestv = v
                best = (x, y)
        return best

    tx, ty = best_target()

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # Also consider taking the resource if we reach it (deterministically via distance 0).
        score = (do2 - ds2) * 120 - ds2 * 3
        # Avoid getting closer to opponent when it doesn't help: small penalty by relative chebyshev.
        my_to_opp = cheb(nx, ny, ox, oy)
        my_from_opp = cheb(sx, sy, ox, oy)
        if my_to_opp < my_from_opp:
            score -= (my_from_opp - my_to_opp) * 8
        # If opponent is near our current target, prioritize minimizing our distance.
        if cheb(ox, oy, tx, ty) <= 2:
            score += max(0, (cheb(sx, sy, tx, ty) - ds2)) * 25
        # Tie-break deterministically: prefer not to move too far (dx*dx+dy*dy smaller), then lexicographic.
        move_pen = dx * dx + dy * dy
        score -= move_pen * 0.01
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]