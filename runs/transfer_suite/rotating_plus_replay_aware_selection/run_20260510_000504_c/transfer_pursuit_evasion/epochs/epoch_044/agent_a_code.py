def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    i_am_pursuer = ("purs" in self_role) or ("chase" in self_role) or ("hunter" in self_role)
    if not i_am_pursuer:
        if ("purs" in opp_role) or ("chase" in opp_role) or ("hunter" in opp_role):
            i_am_pursuer = False
        else:
            i_am_pursuer = ("evad" not in self_role) and ("escap" not in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def clamp_step(dx):
        return -1 if dx < 0 else (1 if dx > 0 else 0)

    dx_to_opp = clamp_step(ox - sx)
    dy_to_opp = clamp_step(oy - sy)

    if i_am_pursuer:
        # Greedy interception: go toward opponent, but penalize increasing distance and obstacle-adjacent "stalls".
        best = None
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            # Prefer moves that also reduce max(|x-ox|,|y-oy|) slightly (smoother approach).
            approach = (abs(ox - sx) + abs(oy - sy)) - (abs(ox - nx) + abs(oy - ny))
            # Small bias: align with direct step direction to prevent dithering.
            align = (1 if dx == dx_to_opp else 0) + (1 if dy == dy_to_opp else 0)
            # Avoid "dead zones": count available neighbor cells from next state.
            neigh_ok = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if valid(tx, ty):
                    neigh_ok += 1
            score = (-d) * 10 + approach * 3 + align * 2 + neigh_ok
            if score > best_score:
                best_score = score
                best = [dx, dy]
        return best if best is not None else [0, 0]
    else:
        # Evader: maximize distance, then steer toward the farthest corner away from pursuer while staying valid.
        far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        fx, fy = far_corner
        best = None
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            # Prefer increasing distance; tie-break by moving toward the chosen far corner.
            prog = (dist2(sx, sy, fx, fy) - dist2(nx, ny, fx, fy))
            # Mild penalty if the move reduces available neighbors (avoid cornering into obstacles).
            neigh_ok = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if valid(tx, ty):
                    neigh_ok += 1
            score = d * 10 + prog * 4 + neigh_ok
            if score > best_score:
                best_score = score
                best = [dx, dy]
        return best if best is not None else [0, 0]