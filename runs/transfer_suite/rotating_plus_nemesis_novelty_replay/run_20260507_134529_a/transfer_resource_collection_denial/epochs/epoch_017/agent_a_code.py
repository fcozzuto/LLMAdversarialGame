def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def best_move_to_target(tx, ty):
        best = (0, 0, -10**9)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            myd = cheb(nx, ny, tx, ty)
            score = -myd
            if score > best[2]:
                best = (dx, dy, score)
        return [best[0], best[1]] if best[2] > -10**9 else [0, 0]

    if not resources:
        return [0, 0]

    # Evaluate each possible move by the best "capture" resource it improves for us.
    best_overall = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        move_val = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            # Prefer resources where we are closer; break ties toward faster pickup.
            # Add a bonus if we can reach no later than opponent.
            adv = opd - myd
            capture_bonus = 6 if myd <= opd else 0
            near_bonus = 0 if myd > 2 else (3 - myd)  # strong push early
            contest_push = 1 if adv >= 0 else 0

            val = adv * 10 + capture_bonus + near_bonus + contest_push * (2 - myd if myd < 2 else 0) - myd
            if val > move_val:
                move_val = val

        # Small deterministic preference for not moving if tied.
        if move_val > best_val or (move_val == best_val and (dx, dy) == (0, 0)):
            best_val = move_val
            best_overall = [dx, dy]

    # If we didn't find any legal moves (should be rare), stay.
    return best_overall if best_val > -10**17 else [0, 0]