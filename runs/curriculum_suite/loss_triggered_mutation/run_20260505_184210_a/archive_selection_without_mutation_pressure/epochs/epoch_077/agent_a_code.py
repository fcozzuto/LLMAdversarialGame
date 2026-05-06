def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        return [0, 0]

    best_key = None
    best_move = (0, 0)
    for dx, dy, nx, ny in legal:
        # Prefer positions that can "steal" a resource before the opponent
        # by maximizing (opponent_dist - our_dist) across all resources.
        max_gain = -10**9
        best_to = None
        for rx, ry in resources:
            opp_d = man(ox, oy, rx, ry)
            our_d = man(nx, ny, rx, ry)
            gain = opp_d - our_d
            if gain > max_gain or (gain == max_gain and (best_to is None or our_d < man(nx, ny, best_to[0], best_to[1]))):
                max_gain = gain
                best_to = (rx, ry)

        # Also discourage moving too close to opponent unless it helps us steal.
        opp_next = man(nx, ny, ox, oy)
        # Key: maximize stealing opportunity, then move closer to the chosen target, then keep distance from opponent.
        # Convert to min-key for determinism.
        target_d = man(nx, ny, best_to[0], best_to[1])
        key = (-max_gain, target_d, opp_next, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]