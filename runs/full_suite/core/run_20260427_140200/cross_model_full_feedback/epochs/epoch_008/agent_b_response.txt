def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    # deterministic set of moves with rotation for variety
    base_moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    rot = turn % len(base_moves)
    moves = base_moves[rot:] + base_moves[:rot]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    best = None
    best_score = -10**9

    me_x, me_y = int(me[0]), int(me[1])
    opp_x, opp_y = int(opp[0]), int(opp[1])

    # helper: resource score for a candidate position
    def resource_score(nx, ny):
        if not resources:
            return 0
        sc = 0
        for rx, ry in resources:
            d_my = dist((nx, ny), (int(rx), int(ry)))
            d_opp = dist((opp_x, opp_y), (int(rx), int(ry)))
            # reward closer to resource than opponent
            sc += (d_opp - d_my)
        return sc

    for dx, dy in moves:
        nx, ny = me_x + dx, me_y + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        # basic safety: don't move into opponent's current cell if possible
        if nx == opp_x and ny == opp_y:
            # allow if no other better move; but prefer not colliding
            pass
        sc = resource_score(nx, ny)

        # encourage approaching nearest resource when available
        if resources:
            nearest = min(resources, key=lambda r: dist((nx, ny), (int(r[0]), int(r[1]))))
            sc += max(0, 5 - dist((nx, ny), (int(nearest[0]), int(nearest[1]))))

        # slight preference to move toward opponent when ahead in score potential
        # If we are farther from nearest resource than opponent, discourage
        opp_to_resource = 0
        if resources:
            nearest_r = min(resources, key=lambda r: dist((opp_x, opp_y), (int(r[0]), int(r[1]))))
            opp_to_resource = dist((opp_x, opp_y), (int(nearest_r[0]), int(nearest_r[1])))
            my_to_resource = dist((nx, ny), (int(nearest_r[0]), int(nearest_r[1])))
            sc += (opp_to_resource - my_to_resource) * 0.1

        if sc > best_score or best is None:
            best_score = sc
            best = (dx, dy)

    if best is None:
        # fallback stay
        return [0, 0]
    return [int(best[0]), int(best[1])]