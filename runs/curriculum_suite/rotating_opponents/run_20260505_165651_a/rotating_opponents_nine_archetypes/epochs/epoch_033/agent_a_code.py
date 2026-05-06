def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def king(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    cx, cy = w // 2, h // 2
    if not resources:
        best = min(valid, key=lambda m: (king(m[2], m[3], cx, cy), abs(m[2]-sx)+abs(m[3]-sy)))
        return [best[0], best[1]]

    best_move = (0, 0, sx, sy)
    best_val = -10**18
    for dx, dy, nx, ny in valid:
        dself_center = king(nx, ny, cx, cy)

        # Primary: maximize the best "takeable" resource advantage after this move.
        # Secondary: minimize how close we allow opponent to steal remaining resources.
        best_adv = -10**9
        opp_threat = 10**9
        steal_block = -10**9
        for rx, ry in resources:
            ds = king(nx, ny, rx, ry)
            do = king(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer than opponent
            if adv > best_adv:
                best_adv = adv
            # Threat for resources the opponent is already close to
            if do < opp_threat:
                opp_threat = do

            # If this resource is currently closer for opponent, try to reduce it (denier strategy)
            if do <= ds:
                # How much closer we make ourselves relative to opponent's ability to reach it next.
                # Slightly prefer moves that reduce opponent's lead across many resources.
                steal_block = max(steal_block, (ds - do) * -1)

        # Encourage "escape from contact" with a small weight; resource_denier can chase.
        contact = king(nx, ny, ox, oy)
        contact_pen = 1.0 if contact <= 1 else (0.3 if contact <= 2 else 0.0)

        val = 4.0 * best_adv + 1.2 * steal_block - 0.9 * opp_threat - contact_pen - 0.05 * dself_center
        if val > best_val:
            best_val = val
            best_move = (dx, dy, nx, ny)

    return [best_move[0], best_move[1]]