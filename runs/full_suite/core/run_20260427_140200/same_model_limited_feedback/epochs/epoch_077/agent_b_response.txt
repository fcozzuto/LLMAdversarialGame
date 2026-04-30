def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
    opp_pos = (ox, oy)

    best_move = [0, 0]
    best_val = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        new_pos = (nx, ny)
        safety = dist(new_pos, opp_pos)
        best_res = -10**9
        for rx, ry in resources:
            r = (rx, ry)
            rd = dist(new_pos, r)
            od = dist(opp_pos, r)
            # Prefer resources where we are (or become) closer than the opponent
            val = (od - rd) * 2.0 - rd * 0.1
            if rd == 0:
                val += 1000.0
            best_res = val if val > best_res else best_res
        total = best_res + safety * 0.2
        if total > best_val:
            best_val = total
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]