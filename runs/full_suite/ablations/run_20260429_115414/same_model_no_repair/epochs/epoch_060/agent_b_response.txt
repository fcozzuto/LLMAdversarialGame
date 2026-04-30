def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Pick a target that favors us relative to the opponent
    best_res = None
    best_val = None
    best_self_d = None
    for r in resources:
        d_s = dist((sx, sy), tuple(r))
        d_o = dist((ox, oy), tuple(r))
        val = d_o - d_s
        if best_val is None or val > best_val or (val == best_val and d_s < best_self_d):
            best_val, best_self_d, best_res = val, d_s, tuple(r)

    tx, ty = best_res
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    grid_w, grid_h = observation.get("grid_width", 8), observation.get("grid_height", 8)

    best_move = [0, 0]
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= grid_w or ny >= grid_h:
            continue
        if (nx, ny) in obstacles:
            continue

        self_d = dist((nx, ny), (tx, ty))
        self_now = dist((sx, sy), (tx, ty))
        opp_d = dist((ox, oy), (tx, ty))

        # Prefer decreasing our distance, and also prefer making it harder for opponent indirectly
        score = (self_now - self_d) * 100 - self_d
        # Slightly prefer central moves when tied (reduce edge trapping)
        score -= 0.1 * (abs((grid_w - 1) / 2 - nx) + abs((grid_h - 1) / 2 - ny))
        # If opponent is close to the target, prioritize faster approach
        if opp_d <= 2:
            score += (2 - opp_d) * 5 - self_d * 2

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If all candidate moves are blocked, stay still
    return best_move if best_score is not None else [0, 0]