def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = gw - 1 - sx, gh - 1 - sy
        if sx < gw - 1: tx = gw - 1
        if sy < gh - 1: ty = gh - 1
    else:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we are relatively closer; tie-break deterministically.
            val = (ds - do * 1.05, (rx + ry) % 8, rx, ry)
            if best is None or val < best[0]:
                best = (val, rx, ry)
        _, tx, ty = best

    # One-step greedy toward chosen target, but keep opponent-advantage in evaluation.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if resources:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            score = (ds - do * 1.05, ds, abs(nx - tx) + abs(ny - ty))
        else:
            score = (cheb(nx, ny, tx, ty), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]