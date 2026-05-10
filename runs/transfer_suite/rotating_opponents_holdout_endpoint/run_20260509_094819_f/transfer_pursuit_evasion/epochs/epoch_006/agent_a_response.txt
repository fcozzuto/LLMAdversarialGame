def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    blocked = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = ("purs" in self_role) or ("evad" in opponent_role and "purs" in self_role) or ("purs" in opponent_role and "purs" in self_role)
    if not self_is_pursuer:
        self_is_pursuer = ("purs" in self_role) or ("purs" in self_role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    opp_on_wall = (ox == 0 or ox == w - 1 or oy == 0 or oy == h - 1)
    wall_axis = 0 if (ox == 0 or ox == w - 1) else 1  # 0: x-wall, 1: y-wall

    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue

        d = dist2((nx, ny), (ox, oy))
        if self_is_pursuer:
            score = (0, -d)
            if opp_on_wall:
                # Block: try to match the wall coordinate (x if opponent on vertical wall, else y)
                if wall_axis == 0:
                    score = (0, -d, -abs(nx - ox))
                else:
                    score = (0, -d, -abs(ny - oy))
            # Prefer not walking away from the center when no wall blocking target exists
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center_bias = -(abs(nx - cx) + abs(ny - cy))
            score = score + (center_bias,)
        else:
            # Evader: maximize distance, then push toward farthest corner deterministically
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            progress = -(abs(far_corner[0] - nx) + abs(far_corner[1] - ny))
            # Wall-run: if opponent is near wall, move along that wall direction
            wall_run = 0
            if opp_on_wall:
                if wall_axis == 0:
                    # vertical wall: try to keep x similar to opponent wall side, vary y
                    wall_run = -abs(nx - ox) * 2 + (abs(ny - oy) * 0.5)
                else:
                    wall_run = -abs(ny - oy) * 2 + (abs(nx - ox) * 0.5)
            score = (d, progress, wall_run)
        if best is None or score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]