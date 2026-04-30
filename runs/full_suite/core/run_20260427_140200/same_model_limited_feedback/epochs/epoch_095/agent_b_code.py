def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b):
        x1, y1 = a
        x2, y2 = b
        dx = x1 - x2
        dy = y1 - y2
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    best_move = [0, 0]
    best_score = None

    resources = observation.get("resources", [])
    have_res = bool(resources)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        if have_res:
            # aim for nearest resource
            md = 10**9
            for r in resources:
                rx, ry = r[0], r[1]
                d = (nx - rx if nx >= rx else rx - nx) + (ny - ry if ny >= ry else ry - ny)
                if d < md:
                    md = d
            # also prefer moving away from opponent to reduce collisions
            opp_pen = dist((nx, ny), (ox, oy))
            score = (-md, -(-opp_pen), -nx * 1000 - ny)  # lexicographic via tuple
        else:
            # drift away from opponent
            dd = dist((nx, ny), (ox, oy))
            score = (dd, -nx * 1000 - ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if (0 <= sx + best_move[0] < w and 0 <= sy + best_move[1] < h and (sx + best_move[0], sy + best_move[1]) not in obs) else [0, 0]