def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def quad_score(p):
        x, y = p
        return (1 if x >= w // 2 else 0) * 2 + (1 if y >= h // 2 else 0)

    if not resources:
        return [0, 0]

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    best = None
    best_sc = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # score: prefer positions that reduce our time-to-resources while making it harder for opponent
        # also prefer upper/right quadrants for some consistent momentum
        our_dmin = 10**9
        opp_dmin = 10**9
        for r in resources:
            d_our = cheb((nx, ny), r)
            if d_our < our_dmin:
                our_dmin = d_our
            d_opp = cheb((ox, oy), r)
            if d_opp < opp_dmin:
                opp_dmin = d_opp
        # If we can step onto a resource this turn, prioritize heavily.
        on_resource = any((nx, ny) == r for r in resources)
        if on_resource:
            sc = 10**6
        else:
            # Opponent-denial bias: advantage grows when we're closer than opponent's closest resource.
            sc = 0
            sc += -4 * our_dmin
            sc += 2 * (opp_dmin - our_dmin)
            # add deterministic quadrant preference based on nearest resource quadrant from our position
            nearest = None
            nd = 10**9
            for r in resources:
                d = cheb((nx, ny), r)
                if d < nd:
                    nd = d
                    nearest = r
            sc += 0.5 * quad_score(nearest)
            # small preference for staying away from opponent if tie-ish
            sc += -0.05 * cheb((nx, ny), (ox, oy))
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]