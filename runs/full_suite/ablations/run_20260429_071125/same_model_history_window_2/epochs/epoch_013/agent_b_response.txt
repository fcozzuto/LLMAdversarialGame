def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) == 2:
            obstacles.add((p[0], p[1]))

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def manh(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx + dy

    def edge_pen(nx, ny):
        return (0.9 if nx == 0 else 0) + (0.9 if nx == w - 1 else 0) + (0.9 if ny == 0 else 0) + (0.9 if ny == h - 1 else 0)

    # If no resources, head to reduce distance to opponent's corner with mild edge avoidance
    if not resources:
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            score = -d_opp - 0.03 * edge_pen(nx, ny)
            cand = (score, abs(nx-ox)+abs(ny-oy), dx, dy)
            if best is None or cand > best:
                best = cand
        if best is None:
            return [0, 0]
        return [best[2], best[3]]

    # Deterministic: consider resources in fixed coordinate order
    res_sorted = sorted((r[0], r[1]) for r in resources)
    best_move = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Find best immediate target advantage at this next position
        best_adv = -10**18
        for rx, ry in res_sorted:
            d_r_now = cheb(sx, sy, rx, ry)
            d_r_next = cheb(nx, ny, rx, ry)
            # Prefer moves that reduce distance to a resource more than the opponent does
            d_o_now = cheb(ox, oy, rx, ry)
            d_o_next = cheb(ox, oy, rx, ry)  # opponent position fixed this turn
            adv = (d_r_now - d_r_next) - 0.15 * (d_r_next - d_o_next)
            # Small bias toward closer resources overall
            adv += 0.01 * (-d_r_next)
            if adv > best_adv:
                best_adv = adv

        # Also prefer keeping some distance from opponent to avoid interference while contesting
        dist_opp = manh(nx, ny, ox, oy)
        score = best_adv + 0.02 * dist_opp - 0.05 * edge_pen(nx, ny)
        cand = (score, -cheb(nx, ny, ox, oy), -manh(nx, ny, ox, oy), dx, dy)
        if best_move is None or cand > best_move:
            best_move = cand

    if best_move is None:
        return [0, 0]
    return [best_move[3], best_move[4]]