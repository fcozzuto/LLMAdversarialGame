def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        m = 0
        for dx, dy in dirs:
            if inb(x + dx, y + dy):
                m += 1
        return m

    # Directional bias away/towards opponent to keep pressure consistent across epochs.
    # Use Chebyshev distance since diagonal moves are allowed.
    best_dxdy = (0, 0)
    best_score = -10**18 if pursuer else 10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_self_to_opp = cheb(nx, ny, ox, oy)
        # Near-capture bias (capture radius 0): exact match is strongest.
        capture_term = 0
        if nx == ox and ny == oy:
            capture_term = 10**9 if pursuer else -10**9

        mob = mobility(nx, ny)
        # If pursuing, avoid low-mobility traps; if evading, prefer high mobility.
        trap_pen = (5 - mob)

        # Optional obstacle-aware bias: discourage stepping into "tight" cells.
        # Tightness approximated by number of blocked neighbors.
        blocked = 0
        for ddx, ddy in dirs:
            tx, ty = nx + ddx, ny + ddy
            if not inb(tx, ty):
                blocked += 1

        if pursuer:
            score = -d_self_to_opp * 1000 + capture_term - trap_pen * 3 - blocked
        else:
            # Move away while keeping mobility; also keep away from opponent as the main goal.
            score = d_self_to_opp * 1000 + capture_term + mob * 2 - trap_pen * 2 - blocked * 0.5

        if pursuer:
            if score > best_score:
                best_score = score
                best_dxdy = (dx, dy)
        else:
            if score < best_score:
                best_score = score
                best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]