def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []

    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0: nx = 0
        if nx >= w: nx = w - 1
        if ny < 0: ny = 0
        if ny >= h: ny = h - 1

        penalty = 0
        if (nx, ny) in obstacles:
            penalty -= 10000

        # Prefer moves that keep us closer to resources and increase opponent distance (deny).
        val = penalty
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            oppd = md(ox, oy, rx, ry)

            # Strongly prioritize resources where we can arrive before the opponent.
            deny_gap = oppd - myd
            arrive_bonus = -0.25 * myd  # quicker pickup
            focus = 2.5 * (deny_gap)  # deny
            # Slightly avoid committing to resources opponent is already essentially winning.
            trap = 1.2 if deny_gap < 0 else 0
            val += focus + arrive_bonus - trap

        # Additional anti-rush: if opponent is very close, bias toward reducing our distance to resources
        # while not stepping onto obstacles.
        if md(nx, ny, ox, oy) <= 2:
            val += 1.0 / (1 + md(nx, ny, ox, oy))

        key = (-val, dx, dy)
        if best_val is None or key < best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]