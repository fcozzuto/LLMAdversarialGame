def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        step_score = -10**18
        for rx, ry in resources:
            sd = md((nx, ny), (rx, ry))
            od = md((ox, oy), (rx, ry))
            # Prefer being earlier than opponent; strong bonus if landing on a resource.
            if (nx, ny) == (rx, ry):
                val = 10**9 - sd
            else:
                val = (od - sd) * 1000 - sd - (rx + ry) * 0.001
            if val > step_score:
                step_score = val

        # Deterministic tie-break: prefer smallest (dx,dy) lexicographically after score.
        if best_score is None or step_score > best_score or (step_score == best_score and (dx, dy) < best_move):
            best_score = step_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]