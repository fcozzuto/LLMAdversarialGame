def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    if not resources:
        dx = 0
        dy = 0
        return [dx, dy]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return max(abs(ax - bx), abs(ay - by))  # king distance

    best = None
    best_key = None
    for r in resources:
        rx, ry = r
        md = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        key = (md - od, md, abs(rx - sx) + abs(ry - sy), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    # prioritize moves that reduce king-distance to target
    best_move = (0, 0)
    best_md = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        md = dist((nx, ny), (tx, ty))
        # also lightly avoid stepping into squares where opponent would be much closer
        opp_md = dist((ox, oy), (tx, ty))
        score = (md, md - opp_md, abs(tx - nx) + abs(ty - ny), -dx, -dy)
        if best_md is None or score < best_score:
            best_md = md
            best_score = score
            best_move = (dx, dy)

    # if all moves blocked, stay
    return [int(best_move[0]), int(best_move[1])]