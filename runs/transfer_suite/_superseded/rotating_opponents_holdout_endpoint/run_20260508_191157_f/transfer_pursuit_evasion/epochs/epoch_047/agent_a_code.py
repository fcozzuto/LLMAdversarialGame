def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    role = observation.get("self_role", "")
    env = observation.get("environment_name", "")
    if env != "pursuit_evasion":
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    # Basic potential: use Chebyshev distance for capture rules.
    def d(x, y):
        ax, ay = x - ox, y - oy
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    def obstacle_penalty(x, y):
        p = 0
        for nx in (x - 1, x, x + 1):
            for ny in (y - 1, y, y + 1):
                if (nx, ny) in obs:
                    # Penalize being close to obstacles (especially immediate neighbors)
                    if abs(nx - x) + abs(ny - y) <= 1:
                        p += 3
                    else:
                        p += 1
        return p

    best = None
    # Deterministic tie-break order: keep-still earlier, then lexicographic.
    ordered = sorted(moves, key=lambda t: (t[0] != 0 or t[1] != 0, t[0], t[1]))
    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        dist = d(nx, ny)
        pen = obstacle_penalty(nx, ny)

        # Pursuer: minimize distance, avoid obstacles; Evader: maximize distance.
        if role == "evader":
            # Also bias away from opponent along dominant axis to break zigzag traps.
            ax = (ox - sx)
            ay = (oy - sy)
            if ax < 0: ax = -ax
            if ay < 0: ay = -ay
            bias = (dx * (-(ox - sx)) + dy * (-(oy - sy)))  # positive when moving away
            score = (-dist, -pen, -bias)
        else:
            # Pursuer role
            # Bias toward moves that reduce both |dx| and |dy| when possible.
            before_x = abs(sx - ox)
            before_y = abs(sy - oy)
            after_x = abs(nx - ox)
            after_y = abs(ny - oy)
            reduce_both = (after_x <= before_x and after_y <= before_y)
            score = (dist, pen, 0 if reduce_both else 1, dx, dy)

        if best is None or score < best[0]:
            best = (score, [dx, dy])

    return best[1] if best is not None else [0, 0]