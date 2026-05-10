def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    role = observation.get("self_role", "pursuer")
    deltas = [(-1, -1), (1, 1), (-1, 1), (1, -1), (-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Corner bias targets for opponent evasion
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def far_corner(x, y):
        return max(corners, key=lambda c: dist2(x, y, c[0], c[1]))

    if role == "evader":
        tx, ty = far_corner(ox, oy)  # run toward the farthest corner from pursuer
        best = None
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = dist2(nx, ny, ox, oy)  # maximize distance
            v += 0.03 * dist2(nx, ny, tx, ty)  # move toward escape corner
            v -= 0.01 * (abs(nx - tx) + abs(ny - ty))  # stabilize ties
            if (nx, ny) == (sx, sy):
                v -= 0.05  # discourage stalling
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Pursuer: 1-step lookahead minimax (deterministic)
    best = None
    bestv = 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # assume opponent moves to maximize its distance from us
        worst = -10**18
        for odx, ody in deltas:
            mx, my = ox + odx, oy + ody
            if not inb(mx, my):
                continue
            d = dist2(nx, ny, mx, my)
            # slight bias: if opponent can reach a corner, prefer that move
            c = far_corner(ox, oy)
            d += 0.02 * dist2(mx, my, c[0], c[1])
            # discourage opponent entering us-adjacent region deterministically (capture radius 0)
            d -= 0.001 * (abs(mx - nx) + abs(my - ny))
            if d > worst:
                worst = d
        # we want to minimize the opponent's best response distance
        v = worst
        # tie-break: prefer moves that also reduce distance directly
        v2 = dist2(nx, ny, ox, oy)
        key = (v, v2, abs(nx - (w - 1)) + abs(ny - (h - 1)) if (ox + oy) > (sx + sy) else abs(nx) + abs(ny))
        if key < bestv if isinstance(bestv, tuple) else True:
            bestv = key
            best = (dx, dy)
        elif isinstance(bestv, tuple) and key == bestv and (dx, dy) < best:
            best = (dx, dy)

    return [best[0], best[1]]