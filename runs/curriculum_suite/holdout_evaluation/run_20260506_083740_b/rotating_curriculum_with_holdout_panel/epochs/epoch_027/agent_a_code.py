def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx = 7 if sx < w - 1 else 0
        ty = 7 if sy < h - 1 else 0
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        for mdx, mdy in moves:
            nx, ny = sx + mdx, sy + mdy
            if valid(nx, ny):
                return [mdx, mdy]
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Assume opponent will focus the closest resource; we deny by maximizing (opp_dist - self_dist)
    best_move = [0, 0]
    best_val = -10**18
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue
        # pick opponent's closest resource (tie -> deterministic by coord)
        target = None
        best_opp = 10**9
        for rx, ry in resources:
            d = man(ox, oy, rx, ry)
            if d < best_opp or (d == best_opp and (rx < target[0] or (rx == target[0] and ry < target[1]))):
                best_opp = d
                target = [rx, ry]
        rx, ry = target
        d_self = man(nx, ny, rx, ry)
        d_opp = best_opp
        # add small tie-break: prefer reducing our own distance to that same target
        val = (d_opp - d_self) * 1000 - d_self
        if val > best_val or (val == best_val and (mdx, mdy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [mdx, mdy]

    # If all moves were invalid (shouldn't happen), stay
    return best_move