def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles or not inb(x, y)

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_opp_next_dist(rx, ry):
        best = 10**9
        for dx, dy in deltas:
            tx, ty = ox + dx, oy + dy
            if blocked(tx, ty):
                continue
            d = man(tx, ty, rx, ry)
            if d < best:
                best = d
        return best if best != 10**9 else man(ox, oy, rx, ry)

    if not resources:
        # Evade: maximize minimum manhattan distance to opponent one-step options
        best_move = (0, 0)
        best_sc = None
        opp_nexts = []
        for dx, dy in deltas:
            tx, ty = ox + dx, oy + dy
            if inb(tx, ty) and (tx, ty) not in obstacles:
                opp_nexts.append((tx, ty))
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                nx, ny = sx, sy
            if not opp_nexts:
                sc = (0, -man(nx, ny, ox, oy))
            else:
                mind = min(man(nx, ny, tx, ty) for tx, ty in opp_nexts)
                sc = (mind, -man(nx, ny, ox, oy))
            if best_sc is None or sc > best_sc:
                best_sc = sc
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    best_move = (0, 0)
    best_sc = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Prefer moves that secure a resource closer than opponent (accounting for opponent's next move),
        # with a fallback to simply getting close.
        best_for_move = None
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = best_opp_next_dist(rx, ry)
            # advantage: larger is better; tie-break closer resource first
            adv = opp_d - self_d
            sc = (adv, -self_d, -man(nx, ny, ox, oy), rx, ry)
            if best_for_move is None or sc > best_for_move:
                best_for_move = sc
        if best_sc is None or best_for_move > best_sc:
            best_sc = best_for_move
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]