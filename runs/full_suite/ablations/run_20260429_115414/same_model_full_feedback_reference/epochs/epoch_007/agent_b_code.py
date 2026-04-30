def choose_move(observation):
    W = observation["grid_width"]; H = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def legal(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def best_resource_value(mx, my):
        if not resources: return -10**12
        best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obs: 
                continue
            md = cheb(mx, my, rx, ry)
            od = cheb(ox, oy, rx, ry)
            tie = 1 if md == od else 0
            # Strongly favor resources we can take no later than opponent; bias toward nearer.
            v = (od - md) * 60 - md * 3
            if md == 0: v += 300
            elif od - md >= 1: v += 35
            if tie == 1: v -= 8
            best = v if v > best else best
        return best

    def opp_next_best(opp_x, opp_y):
        # Opponent best capture value after one move (using current resources).
        if not resources: return -10**12
        best = -10**18
        for ddx, ddy in moves:
            nx, ny = opp_x + ddx, opp_y + ddy
            if not legal(nx, ny): 
                nx, ny = opp_x, opp_y
            val = -10**18
            for rx, ry in resources:
                if (rx, ry) in obs:
                    continue
                d = cheb(nx, ny, rx, ry)
                # value high if opponent can get it quickly (and especially if immediate)
                vv = -d
                if d == 0: vv += 220
                val = vv if vv > val else val
            best = val if val > best else best
        return best

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            nx, ny = sx, sy

        myv = best_resource_value(nx, ny)
        # If opponent can improve their capture after our move, penalize.
        onext = opp_next_best(ox, oy)
        score = myv - onext * 0.25

        # Prefer moves that are valid progress (slight tie-break toward center).
        cx, cy = W // 2, H // 2
        score += -cheb(nx, ny, cx, cy) * 0.01

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]