def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If no info, just move away from opponent toward farthest corner
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: dist((sx, sy), c) - dist((ox, oy), c))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if inb(sx + dx, sy + dy):
            return [dx, dy]
        if inb(sx + dx, sy):
            return [dx, 0]
        if inb(sx, sy + dy):
            return [0, dy]
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_m = (0, 0)

    # Materially different from earlier: greedy "race advantage" for next position + capture bonus
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_pos = (nx, ny)
        opp_pos = (ox, oy)
        score = 0
        # Prefer actions that secure a resource sooner than opponent; also account for capture this turn.
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            rpos = (rx, ry)
            d_my = dist(my_pos, rpos)
            d_opp = dist(opp_pos, rpos)
            # positive if we are closer than opponent; stronger when we can arrive strictly first
            adv = d_opp - d_my
            # capture this turn (resource on our cell)
            cap = 6 if (nx == rx and ny == ry) else 0
            # small discouragement for longer routes
            route = -0.25 * d_my
            score += cap + 2.5 * adv + route
        # Mild tie-break: prefer moving rather than staying, but don't choose illegal moves already handled
        score += -0.05 * (abs(dx) + abs(dy))

        if best is None or score > best:
            best = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]