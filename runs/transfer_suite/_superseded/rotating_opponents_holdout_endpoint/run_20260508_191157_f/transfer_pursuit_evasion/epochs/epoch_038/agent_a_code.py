def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    self_role = observation.get("self_role", "pursuer")

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    deltas.sort(key=lambda t: (abs(t[0]) + abs(t[1]) != 0, t[0], t[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obs_prox(x, y):
        if not obs_set:
            return 99
        best = 10**9
        for ax, ay in obs_set:
            d = abs(ax - x) + abs(ay - y)
            if d < best:
                best = d
                if best <= 1:
                    break
        return best

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: man(c[0], c[1], ox, oy))

    best_delta = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            nx, ny = sx, sy
        d_opp = man(nx, ny, ox, oy)
        d_corner = man(nx, ny, far_corner[0], far_corner[1])
        prox = obs_prox(nx, ny)
        mobility = 0
        for mx, my in deltas:
            tx, ty = nx + mx, ny + my
            if inb(tx, ty) and (tx, ty) not in obs_set:
                mobility += 1

        if self_role == "pursuer":
            val = -d_opp - 0.15 * prox + 0.01 * mobility
        else:
            val = d_opp - 0.15 * prox + 0.01 * mobility + 0.03 * (d_corner)

        if best_val is None or val > best_val:
            best_val = val
            best_delta = [dx, dy]

    return best_delta