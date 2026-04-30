def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose a deterministic priority target: maximize opponent advantage on it.
    best_t = resources[0]
    best_a = -10**18
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        a = (od - sd) * 1000 - sd
        if a > best_a or (a == best_a and (rx, ry) < best_t):
            best_a = a
            best_t = (rx, ry)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    moves.sort(key=lambda t: (abs(t[0]) + abs(t[1]), t[0], t[1]))  # deterministic tie-break

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        our_d = 10**9
        opp_d = 10**9
        for rx, ry in resources:
            d1 = cheb(nx, ny, rx, ry)
            if d1 < our_d: our_d = d1
            d2 = cheb(ox, oy, rx, ry)
            if d2 < opp_d: opp_d = d2
        t_prog = cheb(nx, ny, best_t[0], best_t[1])
        # Main objective: maximize advantage (opponent farther than us), then progress to priority.
        val = (opp_d - our_d) * 120 - our_d * 3 - t_prog * 25
        # Extra: if we're closer to priority than staying, prefer it slightly (path commitment).
        st_t = cheb(sx, sy, best_t[0], best_t[1])
        if t_prog < st_t:
            val += 5
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]