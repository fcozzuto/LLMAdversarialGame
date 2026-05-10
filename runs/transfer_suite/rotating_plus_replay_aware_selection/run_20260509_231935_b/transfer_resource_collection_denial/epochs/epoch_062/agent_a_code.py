def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    res = [(p[0], p[1]) for p in resources if p and len(p) >= 2]
    if not res:
        return [0, 0]
    obs = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(a, b, c, d): 
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    best_adj = None
    for tx, ty in res:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx == tx and ny == ty and inb(nx, ny) and (nx, ny) not in obs:
                best_adj = (tx, ty)
                break
        if best_adj:
            break
    if best_adj:
        tx, ty = best_adj
        dx = tx - sx
        dy = ty - sy
        if dx < -1: dx = -1
        if dx > 1: dx = 1
        if dy < -1: dy = -1
        if dy > 1: dy = 1
        return [dx, dy]

    best = None
    best_score = -10**18
    for tx, ty in res:
        if not inb(tx, ty) or (tx, ty) in obs:
            continue
        myd = md(sx, sy, tx, ty)
        opd = md(ox, oy, tx, ty)
        score = (opd - myd) * 1000 - myd  # prefer resources where we are closer than opponent
        if score > best_score or (score == best_score and (tx, ty) < best):
            best_score = score
            best = (tx, ty)

    tx, ty = best
    cur_my = md(sx, sy, tx, ty)
    cur_op = md(ox, oy, tx, ty)
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd = md(nx, ny, tx, ty)
        opd = cur_op  # opponent moves unknown; hedge by improving our distance and discouraging approach
        val = (cur_my - myd) * 10 - myd - (myd > cur_my) * 2
        if val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val = val
            best_move = [dx, dy]
    return best_move