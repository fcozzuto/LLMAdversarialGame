def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal_from(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                c += 1
        return c

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        # Pick a contest target: prefer where we're closer; otherwise pick the best chance to reduce the gap.
        best_res = None
        best_key = None  # higher is better
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            gap = od - myd  # positive if we're closer
            # key tuple: primary gap, then smaller my distance, then deterministic tie-break by coords
            key = (gap, -myd, -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                best_res = (rx, ry)
        tx, ty = best_res
    else:
        tx, ty = w // 2, h // 2

    # Score each move: reduce distance to target, deny opponent progress, and keep mobility.
    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        myd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        myd_now = cheb(sx, sy, tx, ty)
        # how much closer we get
        gain = myd_now - myd
        # how our move changes advantage; opponent static (no path info), so use absolute advantage proxy
        advantage = od - myd
        mob = legal_from(nx, ny)
        # deterministic tie-break: prefer smaller (nx,ny) lexicographically after scoring
        score = (gain, advantage, mob, -nx, -ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]