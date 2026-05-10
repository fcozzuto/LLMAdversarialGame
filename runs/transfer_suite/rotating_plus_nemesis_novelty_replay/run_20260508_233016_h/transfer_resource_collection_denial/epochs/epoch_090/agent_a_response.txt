def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = {tuple(p) for p in (observation.get("obstacles", []) or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev

    if not resources:
        return [0, 0]

    # Choose a target where we are (ideally) at least as fast as the opponent; otherwise deny slack.
    best_target = None
    best_key = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        slack = op_d - my_d
        key = (-slack, my_d, rx, ry) if slack >= 0 else (0, my_d + (my_d - op_d) * 2, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)
    tx, ty = best_target

    # Evaluate possible moves with obstacle avoidance and race-aware scoring.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        my_d = dist(nx, ny, tx, ty)
        op_d = dist(ox, oy, tx, ty)
        slack = op_d - my_d
        # Primary: maximize slack (race). Secondary: minimize distance to target. Tertiary: approach direction.
        key = (-slack, my_d, abs(tx - nx) + abs(ty - ny), nx, ny)
        candidates.append((key, [dx, dy]))
    if not candidates:
        # Can't move due to obstacles; stay put.
        return [0, 0]
    candidates.sort(key=lambda t: t[0])
    return candidates[0][1]