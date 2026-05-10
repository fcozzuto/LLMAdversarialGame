def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in obstacles}
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obst

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Target: closest resource by Manhattan distance (deterministic tie-break)
    best_res = None
    best_rd = 10**9
    for rx, ry in resources:
        d = man(sx, sy, rx, ry)
        if d < best_rd or (d == best_rd and (rx, ry) < best_res):
            best_rd = d
            best_res = (rx, ry)

    rx, ry = best_res
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        rd = man(nx, ny, rx, ry)
        od = man(nx, ny, ox, oy)
        # Prefer reducing resource distance; also prefer increasing distance from opponent
        score = -rd * 10 + od
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If all moves blocked, stay if legal else move by first legal step
    if best_move == [0, 0]:
        if legal(sx, sy):
            return [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
    return best_move