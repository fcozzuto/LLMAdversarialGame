def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    # Deterministic priority: head to resource that is closer to me than to opponent,
    # with tie-break toward smaller coordinates. If none, move to center region while avoiding obstacles.
    base_moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    rot = turn % len(base_moves)
    moves = base_moves[rot:] + base_moves[:rot]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    me_x, me_y = int(me[0]), int(me[1])
    opp_x, opp_y = int(opp[0]), int(opp[1])

    best = None
    best_score = -10**9

    # evaluate resource-driven score for a candidate position
    def resource_score(nx, ny):
        if not resources:
            return 0
        sc = 0
        for rx, ry in resources:
            rx_i, ry_i = int(rx), int(ry)
            d_my = dist((nx, ny), (rx_i, ry_i))
            d_opp = dist((opp_x, opp_y), (rx_i, ry_i))
            sc += (d_opp - d_my)
        return sc

    for dx, dy in moves:
        nx, ny = me_x + dx, me_y + dy
        if not valid(nx, ny):
            continue
        sc = resource_score(nx, ny)
        # prefer closer to center as tiebreaker
        cx, cy = (w-1)/2.0, (h-1)/2.0
        center_bias = - (abs(nx - cx) + abs(ny - cy))
        total = sc * 2 + center_bias
        if total > best_score:
            best_score = total
            best = (nx, ny)

    if best is None:
        # fallback: stay or move minimally towards center avoiding obstacles
        for dx, dy in moves:
            nx, ny = me_x + dx, me_y + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    nx, ny = best
    return [nx - me_x, ny - me_y]