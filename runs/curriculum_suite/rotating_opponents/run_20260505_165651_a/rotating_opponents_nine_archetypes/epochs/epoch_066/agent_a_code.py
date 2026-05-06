def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    res = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set(tuple(p) for p in obstacles)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if res:
        tx, ty = min(res, key=lambda r: (md(r[0], r[1], ox, oy), md(r[0], r[1], sx, sy)))
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best = None
    bestm = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        # Prefer reducing distance to target; lightly avoid staying adjacent to opponent
        score = md(nx, ny, tx, ty) * 4 + md(nx, ny, ox, oy)
        if best is None or score < best:
            best = score
            bestm = (dx, dy)

    return [bestm[0], bestm[1]]