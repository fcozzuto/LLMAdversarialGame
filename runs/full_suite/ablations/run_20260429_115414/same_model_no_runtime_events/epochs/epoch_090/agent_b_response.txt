def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx = 1 if sx < w - 1 - sx else (-1 if sx > w - 1 - sx else 0)
        ty = 1 if sy < h - 1 - sy else (-1 if sy > h - 1 - sy else 0)
        nx, ny = sx + tx, sy + ty
        if valid(nx, ny):
            return [tx, ty]
        for mx, my in moves:
            if valid(sx + mx, sy + my):
                return [mx, my]
        return [0, 0]

    best_dx, best_dy = 0, 0
    best_val = 10**18
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            continue

        score = 0
        # Lower is better: prefer moves that (1) get us closer to a resource than the opponent,
        # (2) deny opponent advantage, (3) stay away from urgent threats.
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If we're already on a resource, ds=0 -> very desirable.
            gap = ds - do  # negative means we are closer
            # Weight by how urgent the opponent threat is (do small).
            urgency = 1 / (1 + do)
            score += (gap * 10.0) - (urgency * 5.0) + (ds * 0.25)

        # Tie-break: prefer being closer to opponent (to contest) if overall similar,
        # and prefer larger distance from opponent if similar (to avoid being blocked).
        opp_to_next = cheb(nx, ny, ox, oy)
        score += (opp_to_next * 0.01)

        if score < best_val:
            best_val = score
            best_dx, best_dy = mx, my

    return [int(best_dx), int(best_dy)]