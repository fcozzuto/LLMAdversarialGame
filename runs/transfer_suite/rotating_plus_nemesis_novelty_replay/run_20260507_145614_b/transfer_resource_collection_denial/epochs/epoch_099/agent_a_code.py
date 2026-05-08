def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set((p[0], p[1]) for p in obstacles)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    if any(rx == sx and ry == sy for rx, ry in resources):
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        ndx = 0 if sx == tx else (1 if tx > sx else -1)
        ndy = 0 if sy == ty else (1 if ty > sy else -1)
        return [ndx, ndy]

    best = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        immediate = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                immediate = 1000000
                break

        score = -cheb(nx, ny, ox, oy) * 0.01  # tiny bias away from opponent staying close
        for rx, ry in resources:
            du = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Favor taking resources we can reach sooner than opponent; tie-break on shorter du
            cand = (do - du) * 10 - du * 0.1
            # If resource is at our current target line, prefer that direction deterministically
            if ry == sy: cand += 0.05
            if rx == sx: cand += 0.05
            if cand > score:
                score = cand

        score += immediate
        if score > best:
            best = score
            best_move = [dx, dy]

    return best_move