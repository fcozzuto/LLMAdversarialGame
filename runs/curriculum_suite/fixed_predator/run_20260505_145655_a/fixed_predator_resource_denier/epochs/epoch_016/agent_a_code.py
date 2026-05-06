def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    resources_sorted = sorted(resources)
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        # choose target that maximizes win over opponent and also reduces distance
        for rx, ry in resources_sorted:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            # if opponent is closer, heavily penalize; otherwise reward margin and progress
            margin = od - sd
            sc = margin * 10 - sd
            # discourage targets where opponent is very close (denial risk)
            if od <= sd:
                sc -= (sd - od + 1) * 6
            val = max(val, sc)
        # small bias to keep movement toward center of available resources
        val += - (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)) * 0.01

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move