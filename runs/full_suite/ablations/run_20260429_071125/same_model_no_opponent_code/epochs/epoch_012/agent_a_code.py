def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)
    resources = observation.get("resources", [])
    res = set((p[0], p[1]) for p in resources)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = None
    best_move = (0, 0)

    if res:
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            res_here = 1 if (nx, ny) in res else 0
            dres = min(cheb(nx, ny, rx, ry) for (rx, ry) in res)
            dopp = cheb(nx, ny, ox, oy)
            score = (0 if res_here else 1) * 10000 + dres * 10 + dopp
            if best_score is None or score < best_score:
                best_score = score
                best_move = [dx, dy]
    else:
        tx, ty = w // 2, h // 2
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            dopp = cheb(nx, ny, ox, oy)
            score = cheb(nx, ny, tx, ty) * 10 - dopp
            if best_score is None or score < best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move if isinstance(best_move, list) else [0, 0]