def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def risk(x, y):
        r = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    r += 1
        return r

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def cell_key(p):
        # deterministic ordering among equal scores
        return (p[0], p[1])

    best = None
    for dx, dy, nx, ny in moves:
        # Evaluate best resource with an "advantage" metric after this move.
        best_adv = None
        for rx, ry in resources:
            rsx = cheb(nx, ny, rx, ry)
            rox = cheb(ox, oy, rx, ry)
            # Prefer states where we can arrive earlier; also value being closer when close.
            adv = (rox - rsx) * 10 - rsx
            # Mildly discourage stepping away from opponent in tight races:
            adv -= cheb(nx, ny, ox, oy) * 0.02
            if best_adv is None or (adv, -rsx, cell_key((rx, ry))) > (best_adv[0], best_adv[1], best_adv[2]):
                best_adv = (adv, rsx, cell_key((rx, ry)))
        score = best_adv[0] - risk(nx, ny) * 0.6
        cand = (score, -best_adv[1], dx, dy, nx, ny)
        if best is None or cand > best:
            best = cand

    return [int(best[2]), int(best[3])]