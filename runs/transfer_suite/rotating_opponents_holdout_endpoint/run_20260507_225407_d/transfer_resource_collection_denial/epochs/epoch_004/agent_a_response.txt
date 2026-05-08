def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_for_target(tx, ty, px, py):
        sd = cheb(px, py, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # win-like: prefer states where opponent is farther, and closer overall
        return (od - sd) * 100 - sd

    # Pick target with best "advantage" from current state
    best_t = None
    best_v = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        v = score_for_target(rx, ry, sx, sy)
        # small bias toward nearer resources to reduce dithering
        v += 3 if cheb(sx, sy, rx, ry) <= 2 else 0
        if v > best_v:
            best_v = v
            best_t = (rx, ry)
    tx, ty = best_t

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_s = -10**18
    curd = cheb(sx, sy, tx, ty)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        s = score_for_target(tx, ty, nx, ny)
        nd = cheb(nx, ny, tx, ty)
        if nd < curd:
            s += 2
        elif nd > curd:
            s -= 1
        # avoid getting stuck by discouraging staying still when movement can improve
        if dx == 0 and dy == 0:
            s -= 1
        if s > best_s:
            best_s = s
            best_move = [dx, dy]

    return best_move