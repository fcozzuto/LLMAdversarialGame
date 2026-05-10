def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        # diagonal moves allowed => Chebyshev distance is best for obstacle-free
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def best_adv(px, py):
        # positive is good: opponent farther than us
        best = None
        for rx, ry in resources:
            sd = dist((px, py), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            # prioritize large advantage, then closer to us, then deterministic cell ordering
            key = (-(od - sd), sd, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry), sd, od)
        return best

    # Choose move with 2-ply-ish lookahead: after moving, we assume opponent keeps heading
    # but we only re-evaluate advantage from the new position for determinism.
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # If landing on resource, heavily reward
        immediate = 1000 if (nx, ny) in set(tuple(r) for r in resources) else 0

        # Reward moving into more "dominant" resource region
        adv = best_adv(nx, ny)
        key = adv[0]
        sd = adv[2]
        # Slight penalty for staying still to avoid dithering
        stay_pen = 5 if (dx == 0 and dy == 0) else 0
        # Encourage reduction of distance to the currently best resource
        move_key = (-immediate - (100 - sd) + stay_pen, key)
        if best_key is None or move_key < best_key:
            best_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]