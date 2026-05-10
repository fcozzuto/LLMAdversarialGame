def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_is_pursuer = ("purs" in self_role) or (self_role == "pursuer") or ("evad" in opp_role and "purs" in self_role)
    if not self_role:
        self_is_pursuer = False

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    tx_num = 2 * ox + (far_corner[0] - ox)  # = ox + far_corner[0]
    ty_num = 2 * oy + (far_corner[1] - oy)  # = oy + far_corner[1]
    tx = tx_num // 2
    ty = ty_num // 2
    if tx < 0: tx = 0
    if ty < 0: ty = 0
    if tx >= w: tx = w - 1
    if ty >= h: ty = h - 1

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def obstacle_penalty(x, y):
        # Strongly avoid tight corridors next to obstacles (useful vs wall-running).
        pen = 0
        for ax, ay in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1)):
            if (ax, ay) in obs:
                pen += 18
        if pen and (x, y) == (ox, oy):
            pen += 50
        return pen

    best = (10**18, (0, 0))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = dist2(nx, ny, ox, oy)
        d_tar = dist2(nx, ny, tx, ty)
        pen = obstacle_penalty(nx, ny)

        if self_is_pursuer:
            score = d_opp * 6 + d_tar * 2 + pen
        else:
            # Evader: maximize distance to pursuer while still trending to far_corner.
            score = (-d_opp) * 6 + d_tar * 1 + pen

        if score < best[0]:
            best = (score, (dx, dy))
    return [best[1][0], best[1][1]]