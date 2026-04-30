def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    parity_even = (observation.get("turn_index", 0) % 2 == 0)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        opp_d_self = dist((nx, ny), (ox, oy))
        if parity_even:
            # Compete: prioritize resources close to us and also relatively closer to us than opponent.
            val = min((dist((nx, ny), r) - 0.35 * dist((ox, oy), r)) for r in resources)
        else:
            # Switch: try to grab resources where opponent is far (less direct competition).
            val = min((dist((nx, ny), r) + 0.35 * dist((ox, oy), r)) for r in resources)
        val += 0.02 * opp_d_self
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]