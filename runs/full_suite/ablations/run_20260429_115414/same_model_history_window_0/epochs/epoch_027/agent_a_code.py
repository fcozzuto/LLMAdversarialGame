def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])

    obs = set((p[0], p[1]) for p in obstacles if 0 <= p[0] < w and 0 <= p[1] < h)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if resources:
        best = None
        for rx, ry in resources:
            d = abs(rx - sx) + abs(ry - sy)
            if best is None or d < best[0] or (d == best[0] and (rx, ry) < best[1]):
                best = (d, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (w // 2, h // 2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                dist_to_t = abs(tx - nx) + abs(ty - ny)
                dist_opp = abs(ox - nx) + abs(oy - ny)
                moves.append((dist_to_t, -dist_opp, dx, dy, (nx, ny)))

    if not moves:
        return [0, 0]

    # Deterministic tie-break: prefer lower dist_to_t, then higher distance from opponent, then lexicographic next pos.
    moves.sort(key=lambda z: (z[0], z[1], z[4][0], z[4][1]))
    return [moves[0][2], moves[0][3]]