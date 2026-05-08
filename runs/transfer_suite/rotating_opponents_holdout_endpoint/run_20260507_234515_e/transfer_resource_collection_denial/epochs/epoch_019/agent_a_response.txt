def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Prefer capturing first; if cannot, deny by selecting a target that delays opponent more.
    best = None  # (score, dx, dy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in resources:
            return [dx, dy]

        move_score = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            t_self = cheb(nx, ny, rx, ry)
            t_opp = cheb(ox, oy, rx, ry)

            # Sweep-rows bias: if opponent likely advances by rows, prioritize targets with larger
            # row separation from opponent and smaller diagonal-ish distance from us.
            row_sep = abs(ry - oy)

            # Make winning strongly dominant; otherwise maximize opponent delay.
            win_term = (t_opp - t_self) * 10
            delay_term = (t_opp - t_self)
            dist_term = -(t_self + 0.2 * row_sep)

            # Tie-break: prefer closer self even when t_opp == t_self
            tie_term = -0.5 * t_self
            s = win_term + delay_term + dist_term + tie_term
            if s > move_score:
                move_score = s

        if best is None or move_score > best[0]:
            best = (move_score, dx, dy)

    return [best[1], best[2]]