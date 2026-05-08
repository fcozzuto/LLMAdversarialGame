def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    def pos(p, d=(0, 0)):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        if isinstance(p, dict) and "x" in p and "y" in p:
            return int(p["x"]), int(p["y"])
        return d
    sx, sy = pos(observation.get("self_position", [0, 0]))
    ox, oy = pos(observation.get("opponent_position", [0, 0]))
    role = observation.get("self_role", "pursuer")

    obstacles = set()
    for o in observation.get("obstacles") or []:
        x = y = None
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = o[0], o[1]
        elif isinstance(o, dict) and "x" in o and "y" in o:
            x, y = o["x"], o["y"]
        if x is None:
            continue
        try:
            x, y = int(x), int(y)
        except:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def sgn(a):
        return 0 if a == 0 else (1 if a > 0 else -1)

    opp_dx = sgn(ox - sx)
    opp_dy = sgn(oy - sy)

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        d_to_opp = md(nx, ny, ox, oy)
        d_to_farthest_corner = max(md(nx, ny, cx, cy) for cx, cy in corners)
        d_to_nearest_corner = min(md(nx, ny, cx, cy) for cx, cy in corners)

        if role == "evader":
            # maximize separation, but avoid hugging corners too strongly (prevents easy surround)
            score = (d_to_opp * 10.0) + (d_to_farthest_corner * 0.15) - (d_to_nearest_corner * 0.06)
            # bias moving away from the pursuer direction
            score += (-(dx * opp_dx) - (dy * opp_dy)) * 0.2
        else:
            # pursuer: minimize distance; prioritize moves that align with opponent direction
            score = (-d_to_opp * 10.0) + (d_to_nearest_corner * 0.02)
            score += ((dx * opp_dx) + (dy * opp_dy)) * 0.3

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]