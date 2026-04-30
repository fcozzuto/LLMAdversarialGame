def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def clamp(p):
        x, y = p
        if x < 0: x = 0
        if x >= w: x = w - 1
        if y < 0: y = 0
        if y >= h: y = h - 1
        return x, y

    def dist(a, b):
        # squared Euclidean for determinism/speed
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx*dx + dy*dy

    if resources:
        best_res = None
        best_delta = None
        for r in resources:
            d_self = dist((sx, sy), r)
            d_opp = dist((ox, oy), r)
            delta = d_opp - d_self
            if best_res is None or delta > best_delta or (delta == best_delta and (d_self < dist((sx, sy), best_res))):
                best_res = r
                best_delta = delta
        tx, ty = best_res
    else:
        # No resources visible; move toward opponent to force interaction.
        tx, ty = ox, oy

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = clamp((sx + dx, sy + dy))
        if (nx, ny) in obstacles:
            continue
        d_self = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        d_opp = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        score = -d_self + 0.15 * d_opp
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_score is None:
        # All moves blocked; stay if possible, otherwise move to nearest non-obstacle deterministically.
        if (sx, sy) not in obstacles:
            return [0, 0]
        for dx, dy in moves:
            nx, ny = clamp((sx + dx, sy + dy))
            if (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]