def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or [])) if observation.get("obstacles") is not None else set()

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        cur = 0.0
        nearest_pos = 10**9
        nearest_neg = 10**9

        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)

            # Positive when we're earlier/equal; negative when we're later.
            d = od - sd  # >0 => we're behind; <0 => we're ahead (since od - sd)
            # Convert to "advantage": advantage >0 means we are earlier/equal.
            advantage = (od - sd)
            if advantage >= 0:
                # We're at least as fast as opponent: strong preference.
                # Larger when close; also favors picking resources that the opponent can't beat.
                cur += 16.0 / (1 + sd) + 2.0 * min(5, advantage)
                if sd < nearest_pos:
                    nearest_pos = sd
            else:
                # Opponent faster: discourage, but keep slight pressure to block if close.
                penalty = 12.0 / (1 + od)
                cur -= penalty + 2.0 * min(5, -advantage)
                if od < nearest_neg:
                    nearest_neg = od

        # Small shaping: prefer reducing our distance to the best "ahead-or-equal" option.
        if nearest_pos < 10**9:
            cur += 0.05 * (8 - min(8, nearest_pos))
        # If no ahead resources, still head toward least bad (closest opponent-to-lose) with small bias.
        if nearest_pos >= 10**9 and nearest_neg < 10**9:
            cur += 0.02 * (8 - min(8, nearest_neg))

        # Deterministic tie-break: prefer lexicographically smallest move among equals.
        if cur > best_score or (cur == best_score and (best is None or (dx, dy) < best)):
            best_score = cur
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]