def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def manh(x, y): return abs(x - sx) + abs(y - sy)
    def dist(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    if not resources:
        tx = 0 if sx > (W - 1) / 2 else (W - 1)
        ty = 0 if sy > (H - 1) / 2 else (H - 1)
        if ox < (W - 1) / 2: tx = W - 1
        if oy < (H - 1) / 2: ty = H - 1
        resources = [(tx, ty)]

    best_res = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        # Prefer resources we can reach sooner (max opp_d - my_d), then smaller my_d
        key = (-(op_d - my_d), my_d)
        if best_res is None or key < best_res[0]:
            best_res = (key, rx, ry)
    _, tx, ty = best_res[0], best_res[1], best_res[2]

    best_move = (None, None, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        my_d = dist(nx, ny, tx, ty)
        op_d = dist(nx, ny, ox, oy)
        # Primary: minimize my distance to target; Secondary: maximize distance from opponent
        # Tertiary: prefer moves that reduce target manhattan more than opponent
        improvement = (dist(sx, sy, tx, ty) - my_d) - (dist(sx, sy, ox, oy) - op_d)
        key = (my_d, -op_d, -improvement, nx, ny)
        if best_move[0] is None or key < best_move[0]:
            best_move = (key, dx, dy)

    if best_move[1] is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]