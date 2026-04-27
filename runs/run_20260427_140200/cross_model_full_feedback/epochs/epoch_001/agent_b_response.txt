def choose_move(observation):
    # Deterministic simple strategy:
    # 1) Move towards the closest resource not yet collected by either agent.
    # 2) If no resources left, move toward opponent to block or chase.
    # 3) Avoid obstacles by keeping a step that doesn't land on them.
    turn = observation.get("turn_index", 0)
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    me = observation.get("self_position", [0,0])
    opp = observation.get("opponent_position", [0,0])
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])

    def dist(a,b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Build set for quick obstacle check
    obs_set = set((o[0], o[1]) for o in obstacles)

    # Pick closest resource
    best_r = None
    best_d = 10**9
    for r in resources:
        d = dist(me, r)
        if d < best_d:
            best_d = d
            best_r = r

    target = None
    if best_r is not None:
        target = best_r
    else:
        # no resources left; chase opponent
        target = opp

    # Compute best delta toward target, respecting bounds and obstacles
    dx = 0
    dy = 0
    if target:
        if target[0] > me[0]:
            dx = 1
        elif target[0] < me[0]:
            dx = -1
        else:
            dx = 0

        if target[1] > me[1]:
            dy = 1
        elif target[1] < me[1]:
            dy = -1
        else:
            dy = 0

    # If moving into obstacle, try alternate direction
    cand = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0,0)]
    def valid_move(m):
        nx = me[0] + m[0]
        ny = me[1] + m[1]
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            return False
        if (nx, ny) in obs_set:
            return False
        return True

    chosen = None
    for m in cand:
        if valid_move(m):
            chosen = m
            break
    if chosen is None:
        chosen = (0,0)
    return [int(chosen[0]), int(chosen[1])]