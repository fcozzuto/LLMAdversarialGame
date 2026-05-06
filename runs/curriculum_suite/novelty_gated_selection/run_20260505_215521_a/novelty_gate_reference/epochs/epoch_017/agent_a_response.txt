def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)  # Chebyshev

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp = (ox, oy)

    # If no resources are visible, drift to the midpoint to reduce worst-case loss.
    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        bestv = 10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                v = dist((nx, ny), (tx, ty)) - 0.05 * dist((nx, ny), opp)
                if v < bestv:
                    bestv = v
                    best = [dx, dy]
        return best

    # Resource-deny evaluation: prefer moves that get you closer to a resource that is still far from opponent.
    best = [0, 0]
    bestv = 10**18
    res_list = [tuple(r) for r in resources]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        me = (nx, ny)
        # Consider your best opportunity while penalizing giving the opponent an easy pickup.
        opportunity = 10**18
        for r in res_list:
            d_me = dist(me, r)
            d_op = dist(opp, r)
            # Strongly weight opponent distance to deny diagonal probing.
            v = d_me - 1.25 * d_op
            if v < opportunity:
                opportunity = v
        # Also keep some distance from opponent to avoid being "diagonally aligned" into collisions.
        v_final = opportunity - 0.15 * dist(me, opp) + 0.01 * (abs(nx - (w - 1)) + abs(ny - (h - 1)))
        if v_final < bestv:
            bestv = v_final
            best = [dx, dy]

    return best