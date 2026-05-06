def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    if not resources:
        cx, cy = w // 2, h // 2
        best = [0, 0]
        bestv = None
        for dx, dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs: continue
            v = -cheb(nx, ny, cx, cy)
            if bestv is None or v > bestv:
                bestv = v
                best = [dx, dy]
        return best
    candidates = [(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    best_move = [0, 0]
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        best_adv = None
        best_self_d = None
        best_opp_d = None
        # Pick the resource where we create the biggest lead over the opponent.
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if best_adv is None or adv > best_adv or (adv == best_adv and (sd < best_self_d or (sd == best_self_d and od < best_opp_d))):
                best_adv = adv
                best_self_d = sd
                best_opp_d = od
        # Encourage reaching quickly and keeping advantage; slight tie-break toward center.
        center_bias = -cheb(nx, ny, w // 2, h // 2)
        val = (best_adv * 1000) + (-best_self_d * 10) + center_bias
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]