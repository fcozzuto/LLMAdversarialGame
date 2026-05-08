def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except Exception:
            pass

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("chaser" in self_role) or (self_role == "pursuer")

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def boundary_margin(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    best_dxdy = [0, 0]
    if is_pursuer:
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = abs(nx - ox) + abs(ny - oy)
            b = boundary_margin(nx, ny)
            center = abs(nx - cx) + abs(ny - cy)
            # Lower distance is better; keep some margin; avoid extreme cornering
            score = (-d, b, -center, -max(abs(dx), abs(dy)))
            if best_score is None or score > best_score:
                best_score = score
                best_dxdy = [dx, dy]
    else:
        # Evader: maximize distance from pursuer, favor far corners and boundary safety
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        far_corner = max(corners, key=lambda t: abs(t[0] - ox) + abs(t[1] - oy))
        tx, ty = far_corner
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_op = abs(nx - ox) + abs(ny - oy)
            d_corner = - (abs(nx - tx) + abs(ny - ty))
            b = boundary_margin(nx, ny)
            center = abs(nx - cx) + abs(ny - cy)
            # Prioritize distance, then corner progress, then safety
            score = (d_op, d_corner, b, -center, -max(abs(dx), abs(dy)))
            if best_score is None or score > best_score:
                best_score = score
                best_dxdy = [dx, dy]

    return [int(best_dxdy[0]), int(best_dxdy[1])]