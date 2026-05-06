def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}
    res = [(int(p[0]), int(p[1])) for p in resources]
    if not res:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        cur_to_opp = cheb(sx, sy, ox, oy)
        new_to_opp = cheb(nx, ny, ox, oy)
        opp_adv_penalty = 0
        if new_to_opp < cur_to_opp:
            opp_adv_penalty = -1  # discourage moving closer to opponent

        best_margin = -10**9
        best_self_d = 10**9
        best_opp_d = 10**9

        for rx, ry in res:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            margin = opp_d - self_d
            if margin > best_margin or (margin == best_margin and self_d < best_self_d) or (margin == best_margin and self_d == best_self_d and opp_d < best_opp_d):
                best_margin = margin
                best_self_d = self_d
                best_opp_d = opp_d

        center_x = (w - 1) / 2.0
        center_y = (h - 1) / 2.0
        center_dist = abs(nx - center_x) + abs(ny - center_y)

        key = (best_margin + opp_adv_penalty, -best_self_d, -center_dist)
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]