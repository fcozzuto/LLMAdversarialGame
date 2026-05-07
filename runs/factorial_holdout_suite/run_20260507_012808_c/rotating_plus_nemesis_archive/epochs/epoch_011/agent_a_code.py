def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    occ = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = -10**18
    best_move = [0, 0]

    # Choose move that maximizes our lead on the "most winnable" resource,
    # with secondary preference for reducing our nearest distance (and thus tempo).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        max_adv = -10**18
        min_self = 10**18
        min_opp = 10**18
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - self_d
            if adv > max_adv:
                max_adv = adv
            if self_d < min_self:
                min_self = self_d
            if opp_d < min_opp:
                min_opp = opp_d

        # If we can deny quickly (we're close while opponent isn't), prioritize it.
        # Small deterministic tie-break uses move index via dir order.
        score = max_adv * 1000 - min_self * 2 + (min_opp - min_self) * 0.1
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move