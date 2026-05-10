def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corner = min(corners, key=lambda c: abs(ox - c[0]) + abs(oy - c[1]))

    def adj_obs(x, y):
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + ax, y + ay) in obstacles:
                return 1
        return 0

    def step_towards(a, b):
        return 1 if b > a else (-1 if b < a else 0)

    tx = ox + step_towards(ox, corner[0])
    ty = oy + step_towards(oy, corner[1])
    if not inside(tx, ty):
        tx, ty = ox, oy

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        if nx == ox and ny == oy:
            return [dx, dy]

        d_opp = max(abs(nx - ox), abs(ny - oy))  # L_inf
        d_tgt = max(abs(nx - tx), abs(ny - ty))
        d_corner = abs(nx - corner[0]) + abs(ny - corner[1])
        parity = (nx + ny) & 1
        opp_parity = (ox + oy) & 1

        val = (
            -d_opp * 10.0
            - d_tgt * 3.0
            - 0.06 * d_corner
            + 0.10 * adj_obs(nx, ny)
            - 0.15 * (0 if parity == opp_parity else 1)
        )

        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]