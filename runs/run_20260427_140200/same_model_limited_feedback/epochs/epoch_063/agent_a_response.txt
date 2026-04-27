def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set((int(x), int(y)) for x, y in obstacles)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_res_dist(x, y):
        if not resources:
            return 10**9
        bd = 10**9
        for rx, ry in resources:
            dx = rx - x
            dy = ry - y
            d = dx * dx + dy * dy
            if d < bd:
                bd = d
        return bd

    cur_bd = best_res_dist(sx, sy)

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        nb = best_res_dist(nx, ny)
        dprog = cur_bd - nb
        dov = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)

        # Prefer getting closer to resources; slightly prefer staying away from opponent.
        score = (-nb) + 0.25 * dprog + 0.01 * dov
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move