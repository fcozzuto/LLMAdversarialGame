def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    remaining = observation.get("remaining_resource_count", len(resources))

    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(nx, ny): return inb(nx, ny) and (nx, ny) not in blocked

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            legal_moves.append((dx, dy, nx, ny))
    if not legal_moves:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if not resources or remaining <= 0:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None; bestv = -10**18
        for dx, dy, nx, ny in legal_moves:
            v = -cheb((nx, ny), (cx, cy)) - 0.2 * cheb((nx, ny), (ox, oy))
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    best_res = None; best_score = -10**18; best_ours = 10**9
    for rx, ry in resources:
        rd = (rx, ry)
        ours = cheb((sx, sy), rd)
        opp = cheb((ox, oy), rd)
        if ours == 0:
            score = 10**9
        else:
            score = (opp - ours) * 2 - ours - 0.05 * opp
        if score > best_score or (score == best_score and ours < best_ours):
            best_score = score; best_ours = ours; best_res = rd

    tx, ty = best_res
    chosen = (0, 0); bestv = -10**18
    for dx, dy, nx, ny in legal_moves:
        d_ours = cheb((nx, ny), (tx, ty))
        d_opp = cheb((nx, ny), (ox, oy))
        d_opp_after = cheb((ox, oy), (tx, ty))
        v = -d_ours + 0.01 * d_opp + 0.5 * (d_opp_after - cheb((ox, oy), (tx, ty)))
        # tie-breaks: prefer smaller ours distance, then larger opponent distance from our move
        if v > bestv:
            bestv = v; chosen = (dx, dy)
        elif v == bestv:
            if d_ours < cheb((sx + chosen[0], sy + chosen[1]), (tx, ty)):
                chosen = (dx, dy)
            else:
                if d_opp > cheb((sx + chosen[0], sy + chosen[1]), (ox, oy)):
                    chosen = (dx, dy)

    return [chosen[0], chosen[1]]