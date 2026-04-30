def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_move(nx, ny):
        if res:
            best = -10**9
            for tx, ty in res:
                d_me = cheb(nx, ny, tx, ty)
                d_op = cheb(ox, oy, tx, ty)
                advantage = d_op - d_me
                near_pen = 0 if d_me == 0 else (1.0 / (d_me + 1))
                best = max(best, advantage * 100 + near_pen)
            # break ties by preferring closer overall
            d_min = min(cheb(nx, ny, tx, ty) for tx, ty in res)
            return best - d_min * 0.25
        # No resources: drift toward center
        cx, cy = w // 2, h // 2
        d_me = cheb(nx, ny, cx, cy)
        d_op = cheb(ox, oy, cx, cy)
        return (d_op - d_me) * 10 - d_me * 0.1

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Slightly prioritize staying closer to current direction by deterministic tie-break.
    # Use a fixed move ordering already; this avoids randomness.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        val = score_move(nx, ny)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]