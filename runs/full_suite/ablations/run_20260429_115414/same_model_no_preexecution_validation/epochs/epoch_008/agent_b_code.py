def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def legal(nx, ny): return inb(nx, ny) and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not legal(sx, sy):
        for dx, dy in moves:
            if legal(sx + dx, sy + dy):
                return [dx, dy]

    def obstacle_prox(x, y):
        if not obstacles: return 0
        best = 10**9
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best: best = d
            if best == 0: break
        return best

    # Pick a target resource where we are closer than (or can out-race) opponent
    target = None
    best_t = -10**18
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources where opponent is not strictly ahead too much; slight push to nearer ones
        val = (od - sd) - 0.15 * sd - 0.05 * od
        if val > best_t:
            best_t = val
            target = (rx, ry)

    if target is None:
        return [0, 0]

    rx, ry = target
    opp_can_take = (cheb(ox, oy, rx, ry) <= 1)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny): 
            continue

        sd2 = cheb(nx, ny, rx, ry)
        od2 = cheb(ox, oy, rx, ry)

        # If opponent can take target next, prioritize moves that reduce our distance quickly anyway.
        # If we're not gaining, consider moving toward a resource the opponent is further from.
        score = 0
        score += (od2 - sd2) * 3.0
        score -= 0.8 * sd2
        pp = obstacle_prox(nx, ny)
        score -= 0.12 * (0 if not obstacles else (0 if pp > 4 else (6 - pp) * (1 if pp <= 2 else 0.5)))

        # Strongly discourage staying where opponent will likely arrive earlier
        if opp_can_take and sd2 > 1:
            score -= 6.0

        # If at target, prefer to take immediately
        if nx == rx and ny == ry:
            score += 1000.0

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]