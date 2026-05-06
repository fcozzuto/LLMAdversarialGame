def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    if not resources:
        return [0, 0]

    # Choose target that opponent can reach fastest; we try to guard just before it.
    best_r = None
    best_opp_d = None
    for rx, ry in resources:
        d = dist2(ox, oy, rx, ry)
        if best_opp_d is None or d < best_opp_d or (d == best_opp_d and (rx, ry) < best_r):
            best_opp_d = d
            best_r = (rx, ry)

    rx, ry = best_r
    stepx = 0 if rx == ox else (1 if rx > ox else -1)
    stepy = 0 if ry == oy else (1 if ry > oy else -1)
    gx, gy = rx - stepx, ry - stepy  # guard point one step before the resource

    # If guard point is blocked/out, fall back to direct resource
    if not ok(gx, gy):
        gx, gy = rx, ry

    # Score candidate moves: prioritize reaching/contesting guard point, also reduce opponent distance to same target.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_to_guard = dist2(nx, ny, gx, gy)
        opp_to_guard_next = dist2(ox, oy, gx, gy)  # deterministic since we don't predict opponent move
        my_to_res = dist2(nx, ny, rx, ry)
        opp_to_res = dist2(ox, oy, rx, ry)

        # If we can get closer to the contested area than opponent already is, push strongly.
        closer_boost = 500 if my_to_guard < opp_to_guard_next else 0

        # Prefer moves that reduce our distance while increasing opponent's remaining advantage.
        score = (-my_to_guard) - (0.05 * my_to_res) + (0.03 * opp_to_res) + closer_boost

        # Deterministic tie-break by resulting position
        key = (score, -dx, -dy, nx, ny)
        if best is None or key > best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]