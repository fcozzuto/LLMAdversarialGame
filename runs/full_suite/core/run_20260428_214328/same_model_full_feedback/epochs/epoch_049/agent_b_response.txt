def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Move to reduce distance to opponent slightly to avoid being trapped
        best = (-10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny): 
                continue
            val = -man(nx, ny, ox, oy)
            if val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    # Opponent-aware resource targeting: prefer resources where we're relatively closer.
    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # For this candidate, compute best "swing" among resources.
        best_swing = -10**18
        best_dist = 10**18
        best_block = 10**18
        for rx, ry in resources:
            d_self = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # If opponent is closer, discourage; if we can beat them, encourage.
            swing = (d_opp - d_self) * 10 - d_self
            # Tie-break: prefer closer absolute target and prefer moving away from tight trap patterns.
            if swing > best_swing or (swing == best_swing and (d_self < best_dist or (d_self == best_dist and (nx - rx)*(nx - rx) + (ny - ry)*(ny - ry) < best_block))):
                best_swing = swing
                best_dist = d_self
                best_block = (nx - rx)*(nx - rx) + (ny - ry)*(ny - ry)
        # Additional opponent avoidance to reduce collisions near mid
        opp_pen = man(nx, ny, ox, oy)
        # Slightly prefer advancing toward the densest corner opposite initial (static symmetry breaker)
        corner_bias = (nx if sx <= (w-1)//2 else (w-1-nx)) + (ny if sy <= (h-1)//2 else (h-1-ny))
        val = best_swing - 0.05 * opp_pen + 0.001 * corner_bias
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]