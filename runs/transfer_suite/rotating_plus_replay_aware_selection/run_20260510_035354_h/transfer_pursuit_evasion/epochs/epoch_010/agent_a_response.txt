def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    if "purs" in self_role:
        is_pursuer = True
    elif "evad" in self_role:
        is_pursuer = False
    else:
        is_pursuer = ("purs" in opp_role) and ("evad" not in self_role)

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_key = None
    best_move = (0, 0)

    # If evader, prefer farthest corner; if pursuer, prefer moving toward opponent.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: md(c[0], c[1], ox, oy))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = md(nx, ny, ox, oy)
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        if is_pursuer:
            # Primary: minimize distance (capture when d==0). Secondary: avoid staying; tie: lexicographic
            key = (d, stay_pen, dx, dy)
        else:
            # Primary: maximize distance from pursuer. Secondary: avoid staying; tie: far corner progress then lexicographic
            corner_prog = -md(nx, ny, far_corner[0], far_corner[1])
            key = (-d, stay_pen, corner_prog, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]