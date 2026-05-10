def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_is_pursuer = ("purs" in self_role) or (self_role == "pursuer") or ("evad" in opp_role and "purs" in self_role)
    if not self_role:
        self_is_pursuer = False

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def step_toward(tvx, tvy, prefer_toward=True):
        best_move = (0, 0)
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_opp = dist2(nx, ny, ox, oy)
            d_corner = dist2(nx, ny, tvx, tvy)
            if prefer_toward:
                score = d_opp * 3 + d_corner
            else:
                score = d_opp + d_corner * 2
            # Obstacle proximity penalty
            if obstacles:
                md = 10**9
                for ax, ay in obstacles:
                    dd = abs(nx - ax) + abs(ny - ay)
                    if dd < md:
                        md = dd
                if md == 0:
                    score += 10**6
                elif md == 1:
                    score += 1200
                elif md == 2:
                    score += 80
            if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
        return list(best_move)

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    # Evader-corner archetype: opponent wants the farthest corner from us (most likely).
    desired_corner = max(corners, key=lambda c: dist2(c[0], c[1], sx, sy))

    if not self_is_pursuer:
        # Evader: maximize distance from pursuer while also biasing to desired corner
        best_move = (0, 0)
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = dist2(nx, ny, ox, oy) * 3 + dist2(nx, ny, desired_corner[0], desired_corner[1])
            if obstacles:
                md = 10**9
                for ax, ay in obstacles:
                    dd = abs(nx - ax) + abs(ny - ay)
                    if dd < md:
                        md = dd
                if md == 0:
                    score -= 10**9
                elif md == 1:
                    score -= 150
                elif md == 2:
                    score -= 30
            if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]
    else:
        # Pursuer: cut off by moving toward the likely corner while keeping pressure on opponent
        # Use slightly different weighting than pure chase to adapt.
        return step_toward(desired_corner[0], desired_corner[1], prefer_toward=True)