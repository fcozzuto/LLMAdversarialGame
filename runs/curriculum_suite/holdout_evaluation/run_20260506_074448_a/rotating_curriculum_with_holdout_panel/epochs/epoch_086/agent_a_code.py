def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    resources = [(r[0], r[1]) for r in (observation.get("resources") or []) if 0 <= r[0] < w and 0 <= r[1] < h and (r[0], r[1]) not in obstacles]
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def best_for_pos(px, py):
        if not resources:
            return (0, 0, None)
        best_gap = -10**9
        best_selfd = 10**9
        best = None
        for rx, ry in resources:
            sd = manh(px, py, rx, ry)
            od = manh(ox, oy, rx, ry)
            gap = od - sd
            # prioritize: larger gap, then smaller self distance, then deterministic cell tie-break
            if gap > best_gap or (gap == best_gap and (sd < best_selfd or (sd == best_selfd and (rx, ry) < best))):
                best_gap = gap
                best_selfd = sd
                best = (rx, ry)
        return (best_gap, best_selfd, best)

    best_move = (0, 0)
    best_score = -10**18
    any_valid = False

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        any_valid = True
        gap, sd, target = best_for_pos(nx, ny)
        # Denial-aware: also consider if this position reduces opponent's lead to the same target by moving closer to it
        if target is None:
            score = 0
        else:
            od = manh(ox, oy, target[0], target[1])
            # Encourage capturing soon and denying: reward when gap positive, penalize when negative
            score = (gap * 100) - (sd * 2) + (od - sd) * 3
        # Tiny deterministic tie-break: prefer moves that increase x then y
        score = score * 10 + (dx + 1) * 2 + (dy + 1)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if any_valid:
        return [int(best_move[0]), int(best_move[1])]

    # If all moves blocked (shouldn't happen), stay still
    return [0, 0]