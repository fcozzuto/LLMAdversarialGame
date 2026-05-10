def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_gain(px, py):
        if not resources:
            return -10**9
        best = -10**18
        for rx, ry in resources:
            self_d = cheb(px, py, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # primary: win race (opp_d - self_d), secondary: closer to center of "impact"
            gain = (opp_d - self_d) * 10 - self_d
            if gain > best:
                best = gain
        return best

    if not resources:
        return [0, 0]

    # One-step lookahead: choose move maximizing improvement in race advantage
    best_move = (0, 0)
    best_val = -10**18
    base = best_gain(sx, sy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = best_gain(nx, ny)
        # encourage immediate collection if a resource is stepped onto
        if (nx, ny) in resources:
            val += 1000
        # if both are similar, prefer moves that increase distance from opponent
        opp_now = cheb(sx, sy, ox, oy)
        opp_next = cheb(nx, ny, ox, oy)
        val += (opp_next - opp_now) * 2
        # also nudge away from obstacles by favoring fewer "blocked" neighbor options
        blocked = 0
        for adx, ady in moves:
            tx, ty = nx + adx, ny + ady
            if not inb(tx, ty):
                blocked += 1
        val -= blocked * 0.2
        # prefer improvements first, then val, deterministic tie by move order in list
        if (val > best_val) or (val == best_val and (dx, dy) == best_move) or (val > base and val == best_val):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]