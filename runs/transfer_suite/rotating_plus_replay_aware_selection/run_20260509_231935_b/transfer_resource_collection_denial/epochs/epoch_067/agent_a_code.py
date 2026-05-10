def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    turns = observation.get("turns_remaining", 0)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = []
    for p in resources:
        if p and len(p) >= 2:
            res.append((p[0], p[1]))
    if not res:
        return [0, 0]
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_val = -10**18

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        myd0 = dist_cheb(sx, sy, nx, ny)
        score = 0
        local_best = -10**18

        for rx, ry in res:
            md = dist_cheb(nx, ny, rx, ry)
            od = dist_cheb(ox, oy, rx, ry)
            # Prefer resources I can reach strictly earlier within remaining time.
            can = md <= turns
            can_opp = od <= turns
            reach_bonus = 0
            if can and (not can_opp or md < od):
                reach_bonus = 50 + (od - md) * 3
            elif can and can_opp and md == od:
                reach_bonus = 8
            elif can_opp and not can:
                reach_bonus = -30
            # Also prefer generally closer targets.
            closeness = -(md * 2) + (od * 1)
            # Encourage taking nearer-to-center when advantages are similar.
            center_pref = - (abs(rx - cx) + abs(ry - cy)) * 0.02
            val = reach_bonus + closeness + center_pref
            if val > local_best:
                local_best = val

        # Small penalty for wasting steps (discourages staying still unless best).
        local_best -= (0 if myd0 == 0 else 0.2)
        if local_best > best_val:
            best_val = local_best
            best_move = [dx, dy]

    return best_move