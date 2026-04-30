def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    # Choose a target resource where we are currently relatively closer than the opponent.
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Primary: (do - ds) (we want to be earlier / closer)
        # Secondary: favor smaller ds, then deterministic coordinate tie-break.
        score = (do - ds) * 10000 - ds * 7 - (rx * 11 + ry)
        if best is None or score > best[0]:
            best = (score, rx, ry)
    _, tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        ds = man(nx, ny, tx, ty)
        do = man(ox, oy, tx, ty)
        # Progress to target + attempt to keep being earlier than opponent.
        val = -ds * 30 + (do - ds) * 1200

        # Avoid getting too close to obstacle-adjacent cells.
        if obstacles:
            for ex, ey in obstacles:
                ddx = nx - ex
                if ddx < 0: ddx = -ddx
                ddy = ny - ey
                if ddy < 0: ddy = -ddy
                d = ddx if ddx > ddy else ddy
                if d == 0:
                    val -= 10**9
                elif d == 1:
                    val -= 250
                elif d == 2:
                    val -= 70
                elif d == 3:
                    val -= 20

        # Slightly keep some distance from opponent unless we're clearly racing to win.
        opp_d = max(1, man(nx, ny, ox, oy))
        val += (opp_d - 4) * 6

        # Deterministic tie-break by move and position.
        val -= (dx + 1) * 3 + (dy + 1) * 5 + (nx * 2 + ny)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]