def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort()

    # Opponent-avoid/contested-resource scoring:
    # prefer cells where we are closer than opponent to some resource, but avoid picking
    # a resource that is currently also much closer for opponent (diagonal probing).
    def best_value_from(posx, posy):
        best = -10**9
        for rx, ry in resources:
            sd = manh(posx, posy, rx, ry)
            od = manh(ox, oy, rx, ry)
            # advantage term dominates; if opponent is already closer, strongly reduce.
            adv = od - sd
            if adv < 0:
                cont = adv  # negative
            else:
                cont = adv * 2
            # encourage faster progress early
            time_pref = (5 - min(5, sd)) if rem > 4 else (3 - min(3, sd))
            # slightly prefer resources that are not too close to opponent (less contest)
            proximity_pen = (max(0, 8 - od) // 2)
            val = cont * 7 + time_pref * 3 - proximity_pen * 2
            if val > best:
                best = val
        return best

    cur_best = best_value_from(sx, sy)

    best_move = [0, 0]
    best_eval = cur_best - 1  # allow improvements only
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        ev = best_value_from(nx, ny)
        if ev > best_eval:
            best_eval = ev
            best_move = [dx, dy]
    return best_move