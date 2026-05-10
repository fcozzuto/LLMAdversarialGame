def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    candidates = []
    for r in resources:
        rx, ry = r
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # If opponent is closer, prioritize contesting resources that are "more denied".
        candidates.append((od - sd, -sd, rx, ry))
    # Deterministic: sort by deny score first, then closer to us, then coordinates.
    candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3]), reverse=True)
    _, _, tx, ty = candidates[0]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]
    best = None
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
            dx = dy = 0

        # New steering: move toward target, but also avoid "helping" opponent by not moving closer to them.
        self_to_t = dist((nx, ny), (tx, ty))
        opp_to_t = dist((ox, oy), (tx, ty))
        self_to_opp = dist((nx, ny), (ox, oy))
        # Also add small preference to reduce distance to target in Euclidean-ish diagonal way.
        diag = max(abs(nx - tx), abs(ny - ty))

        val = 0
        # If we can reach significantly sooner than opponent, prioritize that.
        val += (opp_to_t - self_to_t) * 100
        # Otherwise keep moving closer anyway, but don't march directly into opponent influence.
        val += (-(self_to_t)) * 10
        val += self_to_opp * 2
        val += (-(diag))

        # Tie-break deterministically by move direction preference (favor toward increasing x then y).
        if val > best_val or (val == best_val and (dx, dy) > (best[0], best[1])):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]