def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    rem = observation["remaining_resource_count"]

    if (sx, sy) in set((r[0], r[1]) for r in resources):
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs_to_center = {(3, 3), (3, 4), (4, 3), (4, 4)}
    center_bias = 1 if (sx, sy) in dirs_to_center else 0

    def clamp_moves(x, y):
        if x < 0 or y < 0 or x >= w or y >= h:
            return False
        if (x, y) in obstacles:
            return False
        return True

    target_resource = None
    if resources:
        best = None
        for rx, ry in resources:
            d = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
            if best is None or d < best[0]:
                best = (d, rx, ry)
        target_resource = (best[1], best[2])

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not clamp_moves(nx, ny):
            continue

        score = 0.0

        # Resource-seeking
        if target_resource is not None:
            tx, ty = target_resource
            dr = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
            score += -dr * 1.2
            # Bonus if landing on any resource
            if (nx, ny) in set((r[0], r[1]) for r in resources):
                score += 1000.0
            # Slightly discourage moving away from the resource cluster center
            if resources:
                cx = sum(r[0] for r in resources) / len(resources)
                cy = sum(r[1] for r in resources) / len(resources)
                dc = (cx - nx) * (cx - nx) + (cy - ny) * (cy - ny)
                score += -dc * 0.02

        # Endgame contest / block
        if rem <= 4:
            da = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
            score += -da * 0.8
            # If close to opponent, prioritize reducing distance further
            if da <= 4:
                score += 20.0

        # Keep near center early (stable deterministic shaping)
        if rem > 4:
            dist_center = (3.5 - nx) * (3.5 - nx) + (3.5 - ny) * (3.5 - ny)
            score += -(dist_center) * (0.01 + 0.01 * center_bias)

        # Deterministic tie-break: prefer moves earlier in deltas list
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move