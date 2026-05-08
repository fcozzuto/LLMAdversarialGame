def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    if not resources:
        return [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        move_val = -10**18
        for rx, ry in resources:
            if not valid(rx, ry):
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if do <= ds:
                cand = (do - ds) * 1000 - ds
            else:
                cand = -(ds - do) * 1000 - ds - 10000
            if cand > move_val or (cand == move_val and (rx, ry) < (nx, ny)):
                move_val = cand

        if move_val > best_val or (move_val == best_val and (dx, dy) < best_move):
            best_val = move_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]