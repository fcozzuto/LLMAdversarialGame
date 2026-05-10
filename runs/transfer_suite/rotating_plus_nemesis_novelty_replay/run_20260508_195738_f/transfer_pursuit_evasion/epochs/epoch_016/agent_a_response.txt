def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    is_pursuer = ("purs" in self_role) or ("purs" in opp_role) or ("evader" not in self_role)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def step_sign(t, v):
        return 0 if t == v else (1 if v > t else -1)

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        # Obstacle "pressure": avoid moving into tight corridors relative to opponent line
        # and prefer staying aligned with the opponent when pursuing.
        align = 0
        if nx == ox or ny == oy:
            align += 2
        if (nx + step_sign(nx, ox), ny + step_sign(ny, oy)) in obstacles:
            align -= 3

        # Corner bias for evader on 8x8: maximize distance to nearest corner while pursuing minimizes it.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        corner_dists = [dist2(nx, ny, cx, cy) for cx, cy in corners]
        far_corner = max(corner_dists)
        near_corner = min(corner_dists)

        # Use a small deterministic tie-break on position parity
        parity = ((nx + ny) & 1)

        if is_pursuer:
            score = -d + 0.5 * align - 0.02 * near_corner - 0.001 * parity
        else:
            score = d + 0.5 * (align) + 0.02 * far_corner - 0.001 * parity

        candidates.append((score, nx, ny, dx, dy))

    if not candidates:
        return [0, 0]

    # Deterministic: sort by score then by nx,ny
    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [candidates[0][3], candidates[0][4]]