def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    gw, gh = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def obst_near(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None  # (score, -win_indicator, tie, dx, dy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy

        near_pen = 0.35 * obst_near(nx, ny)
        win_indicator = 0
        score = -near_pen
        tie = 0

        # Prefer moves that win contested resources (self gets strictly closer),
        # then also minimize our distance to the best resource.
        best_self_d = 10**9
        best_opp_d = 10**9
        best_delta = 0

        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            if self_d < opp_d:
                win_indicator += 1
                score += 6.0 - 0.6 * self_d
                best_delta = max(best_delta, opp_d - self_d)
            else:
                score += -0.05 * self_d + 0.02 * opp_d

            if self_d < best_self_d or (self_d == best_self_d and opp_d < best_opp_d):
                best_self_d, best_opp_d = self_d, opp_d

        score += 0.25 * best_delta
        score += -0.02 * best_self_d

        if best is None or score > best[0] or (score == best[0] and (-win_indicator) > best[1]) or (
            score == best[0] and (-win_indicator) == best[1] and (dx, dy) < (best[3], best[4])
        ):
            best = (score, -win_indicator, tie, dx, dy)

    return [int(best[3]), int(best[4])]