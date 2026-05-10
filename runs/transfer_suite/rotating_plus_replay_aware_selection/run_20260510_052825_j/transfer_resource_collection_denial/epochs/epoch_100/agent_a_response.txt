def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick target resource to maximize "tempo advantage", but also bias to contest
    # resources that opponent can reach quickly (resource_denier).
    best_target = None
    best_tval = None
    for rx, ry in resources:
        if not legal(rx, ry):
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Main: maximize advantage (opponent slower). Secondary: attack resources that are close to both
        # but still keep some pressure when opponent is fast.
        tval = (od - sd, -sd, -(abs(rx - (w - 1)) + abs(ry - (h - 1))), -od)
        if best_tval is None or tval > best_tval:
            best_tval = tval
            best_target = (rx, ry)

    rx, ry = best_target if best_target is not None else resources[0]

    # Choose move that minimizes our distance to target and, if tied, maximizes opponent delay to that same target.
    best_move = (0, 0)
    best_mval = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            nx, ny = sx, sy
        nsd = cheb(nx, ny, rx, ry)
        nod = cheb(ox, oy, rx, ry)
        # Since opponent position doesn't change on our move, nod constant; use it only for tie-break via sd and
        # a mild "stall opponent elsewhere" by encouraging movement that increases distance from opponent to any resource.
        # Keep it cheap: compute max of (opp_dist - our_dist) over a few top resources deterministically.
        stall = 0
        # Deterministic sampling: sort by distance from us; take first up to 3.
        dlist = []
        for pr in resources:
            if legal(pr[0], pr[1]):
                dlist.append((cheb(sx, sy, pr[0], pr[1]), pr[0], pr[1]))
        dlist.sort()
        for _, px, py in dlist[:3]:
            stall = max(stall, cheb(ox, oy, px, py) - cheb(nx, ny, px, py))
        mval = (-nsd, -stall, dx * dx + dy * dy == 0)  # prefer moving over staying when equal
        if best_mval is None or mval > best_mval:
            best_mval = mval
            best_move = (dx, dy)

    dx, dy = best_move
    if not isinstance(dx, int):
        dx = int(dx)
    if not isinstance(dy, int):
        dy = int(dy)
    if dx < -1:
        dx = -1
    if dx > 1:
        dx = 1
    if dy < -1:
        dy = -1
    if dy > 1:
        dy = 1
    return [dx, dy]