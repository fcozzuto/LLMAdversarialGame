def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation.get("opponent_position", (None, None))
    resources = observation.get("resources", []) or []
    obstacles_in = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def mindist_to(point_list, x, y):
        if not point_list:
            return 10**9
        best = 10**9
        for px, py in point_list:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    # Decide target: nearest resource, else center
    if resources:
        tx, ty = min(resources, key=lambda r: (abs(r[0] - sx) + abs(r[1] - sy), r[0], r[1]))
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    opp_point_list = []
    if ox is not None and oy is not None:
        opp_point_list = [(ox, oy)]

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        self_d = abs(tx - sx) + abs(ty - sy)
        new_self_d = abs(tx - nx) + abs(ty - ny)
        res_gain = self_d - new_self_d  # positive is better (closer to target)
        opp_d = mindist_to(opp_point_list, sx, sy)
        new_opp_d = mindist_to(opp_point_list, nx, ny)
        # Encourage keeping distance from opponent while moving toward target
        score = 10 * res_gain + (new_opp_d - opp_d)
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    if best_move == (0, 0):
        # If all moves blocked, stay (validator expects a valid move)
        return [0, 0]
    return [best_move[0], best_move[1]]