def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        d_self = dist((sx, sy), (rx, ry))
        d_opp = dist((ox, oy), (rx, ry))
        # Prefer resources closer to us, and penalize those much closer to opponent
        score = (d_self * 2) - (d_opp) + (0.01 * (rx + ry))
        key = (score, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))

    tx, ty = best[1]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = []
    # Deterministic preference: diagonal that moves closer, then axis, then keep
    cand = [(dx, dy), (dx, 0), (0, dy), (0, 0), (-dx, dy), (dx, -dy), (-dx, 0), (0, -dy)]
    seen = set()
    for mx, my in cand:
        if (mx, my) in seen:
            continue
        seen.add((mx, my))
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            # Must not get farther in both dimensions; allow slight moves due to obstacles
            nd = dist((nx, ny), (tx, ty))
            moves.append((nd, mx, my))

    if not moves:
        return [0, 0]

    moves.sort(key=lambda t: (t[0], t[1], t[2]))
    return [int(moves[0][1]), int(moves[0][2])]