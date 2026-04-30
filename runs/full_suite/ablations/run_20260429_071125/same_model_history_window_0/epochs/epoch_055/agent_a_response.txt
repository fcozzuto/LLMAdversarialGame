def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    if not resources:
        tx, ty = ox, oy
    else:
        best = None
        best_lead = None
        best_selfd = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = dist((sx, sy), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            lead = od - sd
            if best is None or lead > best_lead or (lead == best_lead and (best_selfd is None or sd < best_selfd)):
                best = (rx, ry)
                best_lead = lead
                best_selfd = sd
        tx, ty = best if best is not None else resources[0]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = (0, 0)
    bestscore = None
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            score = 10**9
        else:
            nd = dist((nx, ny), (tx, ty))
            td = dist((sx, sy), (tx, ty))
            oppd = dist((ox, oy), (tx, ty))
            my_future_lead = oppd - nd
            center_bias = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
            score = nd * 10 - my_future_lead * 3 + (center_bias * 0.01) + (0 if nd < td else 0.1)
        if bestscore is None or score < bestscore:
            bestscore = score
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]