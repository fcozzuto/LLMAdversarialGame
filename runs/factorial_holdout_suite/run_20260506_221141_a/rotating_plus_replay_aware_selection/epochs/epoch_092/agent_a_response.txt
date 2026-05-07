def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = gw - 1 if sx < gw // 2 else 0
        ty = gh - 1 if sy < gh // 2 else 0
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            v = -d
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Target the resource where we can beat opponent most; if they are ahead, steer to contest.
    opp_weight = 1.35
    best_move, best_val = [0, 0], -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = 0.0
        # Prefer immediate pickup
        if (nx, ny) in obstacles:
            v -= 1000.0
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Beat-opponent term (positive if we are closer)
            beat = (d_opp - d_self)
            # Prefer nearer resources overall; small tie-break on our advantage
            v += (beat * 2.0 - d_self * 0.35) * (1.0 + 0.25 * (beat > 0))
            # If opponent is already extremely close, reduce focusing and instead contest nearer ones
            if d_opp == 0:
                v -= opp_weight * d_self
        # Mild preference to avoid getting stuck: prefer cells with more legal exits
        exits = 0
        for ex, ey in moves:
            ax, ay = nx + ex, ny + ey
            if legal(ax, ay):
                exits += 1
        v += exits * 0.03
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]