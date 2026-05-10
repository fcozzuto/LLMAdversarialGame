def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    self_pos = observation["self_position"]
    opp_pos = observation["opponent_position"]
    obstacles = set((o[0], o[1]) for o in observation.get("obstacles", []))
    sx, sy = self_pos
    ox, oy = opp_pos
    self_role = observation.get("self_role", "")
    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    def clamp_move(nx, ny):
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return True
        return False

    def cheb(a, b, c, d):
        da = abs(a - c)
        db = abs(b - d)
        return da if da > db else db

    candidates = []
    for dx in dxs:
        for dy in dys:
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if not clamp_move(nx, ny):
                continue
            if dx == 0 and dy == 0 and (sx, sy) in obstacles:
                continue
            candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    pursuer = ("pursuer" in self_role.lower()) or (self_role.lower() == "pursuer")
    if pursuer:
        # Greedy: minimize Chebyshev distance to opponent; avoid stepping onto opponent if possible.
        best = None
        best_d = None
        for dx, dy, nx, ny in candidates:
            dist = cheb(nx, ny, ox, oy)
            if (nx, ny) == (ox, oy):
                score = (-1, dist, abs(dx) + abs(dy), dx, dy)
            else:
                score = (0, dist, abs(dx) + abs(dy), dx, dy)
            if best is None or score < best:
                best = score
                best_d = dist
                best_move = [dx, dy]
        return best_move
    else:
        # Evader: maximize distance from pursuer, prefer moving toward the corner farthest from pursuer.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        far_corner = None
        far_score = -1
        for cx, cy in corners:
            d = cheb(cx, cy, ox, oy)
            if d > far_score:
                far_score = d
                far_corner = (cx, cy)
        cx, cy = far_corner

        best = None
        for dx, dy, nx, ny in candidates:
            dist = cheb(nx, ny, ox, oy)
            corner_dist = cheb(nx, ny, cx, cy)
            # Primary: maximize separation; Secondary: progress to farthest corner; Tertiary: avoid getting close.
            if (nx, ny) == (ox, oy):
                score = (-999999, 999999, 0, dx, dy)
            else:
                score = (dist, -corner_dist, abs(dx) + abs(dy), dx, dy)
            if best is None or score > best:
                best = score
                best_move = [dx, dy]
        return best_move