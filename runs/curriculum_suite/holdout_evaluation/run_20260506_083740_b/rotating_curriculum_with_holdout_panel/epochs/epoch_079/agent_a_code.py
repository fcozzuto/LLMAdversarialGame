def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    ob = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                ob.add((x, y))

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    resources = [p for p in (observation.get("resources", []) or []) if p and len(p) >= 2]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best_r = None
        best_d = 10**9
        for p in resources:
            rx, ry = int(p[0]), int(p[1])
            if valid(rx, ry):
                d = abs(rx - sx) + abs(ry - sy)
                if d < best_d:
                    best_d = d
                    best_r = (rx, ry)
    else:
        best_r = ((w - 1) // 2, (h - 1) // 2)

    best_move = (0, 0)
    best_score = -10**18
    tx, ty = best_r

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_target = abs(tx - nx) + abs(ty - ny)
        d_to_opp = abs(ox - nx) + abs(oy - ny)
        d_opp_now = abs(ox - sx) + abs(oy - sy)
        near_resource = 1 if any(int(p[0]) == nx and int(p[1]) == ny for p in resources) else 0
        score = (-d_to_target) + (0.15 * d_to_opp) + (0.25 * (d_opp_now - d_to_opp)) + (2.0 * near_resource)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]