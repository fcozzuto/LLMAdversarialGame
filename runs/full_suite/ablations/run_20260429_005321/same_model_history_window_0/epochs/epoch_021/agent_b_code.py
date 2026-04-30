def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Dynamic target: resource where we have the biggest "closeness edge"
    best_r = None
    best_edge = None
    for r in resources:
        edge = d2((ox, oy), r) - d2((sx, sy), r)
        if best_edge is None or edge > best_edge:
            best_edge = edge
            best_r = r

    if best_r is None:
        return [0, 0]

    # Opponent current focus (nearest resource) for mild blocking pressure
    opp_t = resources[0]
    best_do = None
    for r in resources:
        dd = d2((ox, oy), r)
        if best_do is None or dd < best_do:
            best_do = dd
            opp_t = r

    tx, ty = best_r
    ox_t, oy_t = opp_t

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_curr_d = d2((ox, oy), (sx, sy))
    best_move = (0, 0)
    best_val = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Core: get closer to our contested target
        v = -d2((nx, ny), (tx, ty))
        # Safety: keep distance from opponent to reduce steals
        v += 0.35 * d2((nx, ny), (ox, oy))
        # Blocking: discourage moving where opponent is already converging
        v += -0.10 * d2((nx, ny), (ox_t, oy_t))
        # If we are currently not ahead on distances, be more defensive
        if best_edge is not None and best_edge < 0:
            v += 0.15 * (d2((nx, ny), (ox, oy)) - opp_curr_d)
        if best_val is None or v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]