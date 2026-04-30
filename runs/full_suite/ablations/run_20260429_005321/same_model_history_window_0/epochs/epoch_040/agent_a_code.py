def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    if resources:
        best = None
        for rx, ry in resources:
            d = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
            if best is None or d < best[0] or (d == best[0] and (rx, ry) < best[1]):
                best = (d, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = ox, oy  # no resources: move to pressure opponent

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dist = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        oppdist = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        # Prefer getting closer to target; if tied, keep away from opponent to avoid interference
        score = dist * 4 - oppdist
        if bestm is None or score < bestm[0] or (score == bestm[0] and (dx, dy) < bestm[1]):
            bestm = (score, (dx, dy))

    if bestm is None:
        return [0, 0]
    return [int(bestm[1][0]), int(bestm[1][1])]