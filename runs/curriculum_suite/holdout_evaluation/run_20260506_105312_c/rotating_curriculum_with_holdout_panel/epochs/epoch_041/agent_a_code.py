def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def block(x, y):
        return (x, y) in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best_t = None
    best_val = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        val = (oppd - myd) * 10 - myd  # secure early and deny
        if val > best_val:
            best_val = val
            best_t = (rx, ry)

    tx, ty = best_t
    # If opponent is closer to all good targets, switch to denial: maximize opponent's distance to chosen target
    myd0 = cheb(sx, sy, tx, ty)
    oppd0 = cheb(ox, oy, tx, ty)
    denial_mode = oppd0 < myd0

    best_move = [0, 0]
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or block(nx, ny):
                continue
            myd = cheb(nx, ny, tx, ty)
            oppd = cheb(ox, oy, tx, ty)
            # Denial effect: prefer moves that move me away from areas that let me be "caught" into losing resources
            # Also slightly encourage moving toward resources closer to me than opponent.
            score = 0
            score += (myd0 - myd) * 25
            score += (oppd - oppd0) * (-5)
            if denial_mode:
                score += (myd - oppd) * 8  # if I'm behind, increase my buffer from target
            # obstacle proximity penalty (stay off tight corners)
            adj_blocks = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    px, py = nx + ax, ny + ay
                    if (ax != 0 or ay != 0) and inb(px, py) and block(px, py):
                        adj_blocks += 1
            score -= adj_blocks * 2
            # break ties deterministically by preferring straight then diagonal then stay
            tie = 0
            if dx == 0 and dy == 0:
                tie = 3
            elif dx == 0 or dy == 0:
                tie = 0
            else:
                tie = 1
            score -= tie * 0.01
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move