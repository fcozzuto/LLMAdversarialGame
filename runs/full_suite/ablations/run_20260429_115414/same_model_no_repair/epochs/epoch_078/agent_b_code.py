def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    res = observation.get("resources", [])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    if not res:
        return [0, 0]

    obs_set = set((x, y) for x, y in obstacles)

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    nearest_now = min((abs(rx - sx) + abs(ry - sy), rx, ry) for rx, ry in res)[0]

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue

        nearest_after = min(abs(rx - nx) + abs(ry - ny) for rx, ry in res)
        dist_to_opp = abs(ox - nx) + abs(oy - ny)

        # Prefer getting closer to some resource, avoid moving adjacent to opponent,
        # and discourage no-improvement moves.
        score = nearest_after * 10
        score += 3 if (dist_to_opp <= 1) else 0
        score += 2 if nearest_after >= nearest_now else 0

        # Deterministic tie-breaking: lexicographic move order via scores + later compare.
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            if [dx, dy] < best_move:
                best_move = [dx, dy]

    return best_move