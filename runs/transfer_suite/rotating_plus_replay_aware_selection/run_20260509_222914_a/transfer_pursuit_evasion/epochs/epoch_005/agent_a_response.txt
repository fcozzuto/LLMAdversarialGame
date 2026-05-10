def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    role = observation.get("self_role", "pursuer")
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corners = [c for c in corners if c not in obstacles] or [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def d_cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
    def best_corner_target(far_from):
        best = None
        for c in corners:
            d = d_cheb(far_from, c)
            if best is None or d > best[0]:
                best = (d, c)
        return best[1]
    self_pt = (x, y)
    opp_pt = (ox, oy)
    target_corner = best_corner_target(self_pt if role == "pursuer" else opp_pt)
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        np = (nx, ny)
        to_opp = d_cheb(np, opp_pt)
        to_corner = d_cheb(np, target_corner)
        # pursuer: minimize both opponent distance and distance to cut-off corner
        # evader: maximize distance to opponent, and head toward corner
        if role == "pursuer":
            val = -10 * to_opp - 1.5 * to_corner + 0.2 * (d_cheb(self_pt, opp_pt) - to_opp)
        else:
            val = 10 * to_opp + 1.5 * (-to_corner)  # effectively minimize corner distance (head to it)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]