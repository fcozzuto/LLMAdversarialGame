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
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Local 1-step lookahead: maximize the best "being-ahead" margin on any resource,
    # and tie-break by keeping our path shorter.
    best_move = (None, -10**9, 10**9)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue

            local_best = -10**9
            local_self = 10**9
            for rx, ry in resources:
                sd_ns = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                ahead = od - sd_ns  # positive means we are closer than opponent
                # Encourage denying: strongly prefer moves that make us clearly closer.
                score = ahead * 30 - sd_ns * 1.0 - (rx + ry) * 0.0001
                if score > local_best or (score == local_best and sd_ns < local_self):
                    local_best = score
                    local_self = sd_ns

            # Small extra pressure to avoid giving up: favor smaller distance even if behind.
            local_best -= man(nx, ny, ox, oy) * 0.001

            if local_best > best_move[1] or (local_best == best_move[1] and local_self < best_move[2]):
                best_move = ((dx, dy), local_best, local_self)

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0][0]), int(best_move[0][1])]