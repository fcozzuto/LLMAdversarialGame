def choose_move(observation):
    W = observation["grid_width"]; H = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)
    res = [(p[0], p[1]) for p in resources if p and len(p) >= 2 and (p[0], p[1]) not in obs]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def legal(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    # If no resources, maximize distance from opponent (safer endgame).
    if not res:
        best = (-10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            d = cheb(nx, ny, ox, oy)
            if d > best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Immediate threat: resources opponent can reach in 1 (capture next turn).
    opp_threat = set()
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if legal(nx, ny):
            for rx, ry in res:
                if cheb(nx, ny, rx, ry) == 0:
                    opp_threat.add((rx, ry))
    # Also include resources within cheb<=1 of opponent (likely capture/claim).
    for rx, ry in res:
        if cheb(ox, oy, rx, ry) <= 1:
            opp_threat.add((rx, ry))

    best_val = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # My closest resource after moving
        my_min = 10**9
        target = None
        for rx, ry in res:
            d = cheb(nx, ny, rx, ry)
            if d < my_min:
                my_min = d; target = (rx, ry)

        # Opponent pressure on that target: how much closer opponent is.
        opp_d_to_target = cheb(ox, oy, target[0], target[1]) if target else cheb(nx, ny, ox, oy)

        # If we can grab a resource now (standing on it), prioritize heavily.
        now_capture = 1 if (nx, ny) in res else 0

        # Contest threatened resources: if our move reduces distance to any threatened resource.
        contest_bonus = 0
        if opp_threat:
            best_th = 10**9
            for rx, ry in opp_threat:
                d = cheb(nx, ny, rx, ry)
                if d < best_th: best_th = d
            # Compare against opponent's ability to still reach them effectively.
            opp_best_th = 10**9
            for rx, ry in opp_threat:
                d = cheb(ox, oy, rx, ry)
                if d < opp_best_th: opp_best_th = d
            # More bonus when we are at/near threatened resources while opponent is not farther behind.
            contest_bonus = 800 - best_th * 150 - max(0, opp_best_th - best_th) * 20

        # Also discourage moving into being adjacent to opponent while we haven't secured a resource.
        being_adjacent = 1 if cheb(nx, ny, ox, oy) <= 1 else 0

        # Value: capture now, otherwise minimize my distance while preventing opponent advantage.
        val = now_capture * 1000000 + (-my_min * 220) + (opp_d_to_target - my_min) * 50 + contest_bonus - being_adjacent * 120
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]