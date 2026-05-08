def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # deterministic prefer diagonal progress first, then straight, then stay
    moves.sort(key=lambda d: (abs(d[0]) == 0, abs(d[1]) == 0, d[0], d[1]))

    best_move = [0, 0]
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)
        man = abs(nx - ox) + abs(ny - oy)

        # If pursuer: minimize distance; if evader: maximize distance.
        # Tie-breaker uses manhattan and a small bias to avoid getting "stuck" by obstacles.
        if is_evader:
            primary = d
            tie = (man, nx, ny)
            val = (primary, ) + tuple(-t for t in tie)  # reverse for max via lexicographic on negatives
        else:
            primary = d
            tie = (man, nx, ny)
            val = (-(primary), ) + tuple(t for t in tie)

        if best is None or val > best:
            best = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]